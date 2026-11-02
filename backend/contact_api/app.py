"""786 Solution contact-only FastAPI service. Set SMTP configuration in cPanel."""
import logging
import os
import smtplib
import ssl
import time
from collections import defaultdict
from email.message import EmailMessage
from threading import Lock

from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, EmailStr, Field

log = logging.getLogger("contact-api")
app = FastAPI(title="786 Solution Contact API", docs_url=None, redoc_url=None, openapi_url=None)
origins = [s.strip().rstrip("/") for s in os.getenv("CONTACT_ALLOWED_ORIGINS", "").split(",") if s.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])

_lock = Lock()
_attempts: dict[str, list[float]] = defaultdict(list)
WINDOW = 900
LIMIT = 5


class ContactRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(default="", max_length=40)
    subject: str = Field(default="", max_length=160)
    message: str = Field(min_length=10, max_length=5000)
    website: str = Field(default="", max_length=180)


def mail_settings() -> dict[str, str]:
    required = ("SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD", "SMTP_FROM", "CONTACT_TO")
    conf = {key: os.getenv(key, "").strip() for key in required}
    if not all(conf.values()):
        raise HTTPException(503, detail="Online contact form unavailable. Please email us directly.")
    security = os.getenv("SMTP_SECURITY", "starttls").strip().lower()
    if security not in ("starttls", "ssl"):
        raise HTTPException(503, detail="Contact service temporarily unavailable.")
    try:
        port = int(os.getenv("SMTP_PORT", "465" if security == "ssl" else "587"))
        if not 1 <= port <= 65535:
            raise ValueError("invalid port")
    except ValueError as exc:
        raise HTTPException(503, detail="Contact service temporarily unavailable.") from exc
    conf["security"] = security
    conf["port"] = str(port)
    return conf


def rate_limit(ip: str) -> None:
    now = time.monotonic()
    with _lock:
        recent = [t for t in _attempts[ip] if now - t < WINDOW]
        if len(recent) >= LIMIT:
            raise HTTPException(429, detail="Too many requests. Please try again later.")
        recent.append(now)
        _attempts[ip] = recent
        if len(_attempts) > 2000:
            for key in list(_attempts):
                valid = [t for t in _attempts[key] if now - t < WINDOW]
                if valid:
                    _attempts[key] = valid
                else:
                    del _attempts[key]


def deliver(data: ContactRequest, conf: dict[str, str]) -> None:
    mail = EmailMessage()
    mail["From"] = conf["SMTP_FROM"]
    mail["To"] = conf["CONTACT_TO"]
    mail["Reply-To"] = str(data.email)
    mail["Subject"] = "786 Solution: New website contact request"
    mail.set_content(
        "New website inquiry\n\n"
        f"Name: {data.name}\nEmail: {data.email}\n"
        f"Phone: {data.phone or 'Not provided'}\n"
        f"Subject: {data.subject or 'General inquiry'}\n\n"
        f"Message:\n{data.message}\n"
    )
    context = ssl.create_default_context()
    port = int(conf["port"])
    if conf["security"] == "ssl":
        with smtplib.SMTP_SSL(conf["SMTP_HOST"], port, timeout=15, context=context) as smtp:
            smtp.login(conf["SMTP_USERNAME"], conf["SMTP_PASSWORD"])
            smtp.send_message(mail)
    else:
        with smtplib.SMTP(conf["SMTP_HOST"], port, timeout=15) as smtp:
            smtp.ehlo()
            smtp.starttls(context=context)
            smtp.ehlo()
            smtp.login(conf["SMTP_USERNAME"], conf["SMTP_PASSWORD"])
            smtp.send_message(mail)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/contact")
async def contact(data: ContactRequest, request: Request) -> dict[str, str | bool]:
    # Hidden honeypot should always be blank for human visitors.
    if data.website:
        return {"ok": True, "message": "Request received."}
    length = request.headers.get("content-length")
    if length:
        try:
            if int(length) > 12000:
                raise HTTPException(413, detail="Message too large.")
        except ValueError as exc:
            raise HTTPException(400, detail="Invalid content length.") from exc
    conf = mail_settings()
    rate_limit(request.client.host if request.client else "unknown")
    try:
        await run_in_threadpool(deliver, data, conf)
    except (OSError, smtplib.SMTPException):
        log.exception("SMTP delivery error")
        raise HTTPException(503, detail="Message could not be delivered. Please email us directly.") from None
    return {"ok": True, "message": "Message sent successfully."}
