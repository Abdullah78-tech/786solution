# 786 Solution contact API — Spaceship deployment

The website form at `timer-html-master/contact.html` sends POST JSON requests to
`https://api.786solution.com/contact`. The API is a separate CloudLinux
Python 3.12 application; do not edit or restart the KHAN Trading application.

## Status (4 November 2026)

- Live `/health` returned HTTP 200 after the LiteSpeed/LSWSGI per-worker initialization fix.
- Contact POST returned HTTP 200, and a browser submission showed the expected success state.
- IMAP inbox search found two messages with the API's subject since 4 November 2026.
- Inbox message identity/timestamps, ongoing uptime, and deliverability to every destination are not yet fully audited.

## Application setup

- Application root: `apps/786solution-contact-api`
- Startup file: `passenger_wsgi.py`
- WSGI entry point: `application`
- Python: 3.12, with dependencies installed from `requirements.txt`.
- The adapter **must** be initialized lazily per worker PID. Creating
  `ASGIMiddleware(app)` at module import can deadlock after LiteSpeed forks
  because the background asyncio thread is not carried into forked workers.
- If cPanel environment variables are not inherited by `lswsgi`, the
  entrypoint supports an optional private file:
  `~/.config/786solution-contact-api/smtp.ini`
  with a section `[smtp]` and variable names below as INI keys.
  Store the file **outside the web root and Git repository**; restrict the
  directory to mode `700` and file to `600`. Never commit its contents.

## Configuration

- `SMTP_HOST`
- `SMTP_PORT` (465 for SSL)
- `SMTP_SECURITY` (`ssl` or `starttls`)
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_FROM`
- `CONTACT_TO`

The app also supports `CONTACT_ALLOWED_ORIGINS` as a comma-separated list.
If the environment variable is absent, the two production origins are the
defaults: `https://786solution.com` and
`https://www.786solution.com`. Only allow additional origins deliberately.

## Safe checks after a deployment

1. Run `python -m py_compile app.py passenger_wsgi.py` in the app virtualenv.
2. Restart **only** the 786solution Python App in cPanel.
3. Request `https://api.786solution.com/health`: expect `200` and
   `{"status":"ok"}`.
4. Send an OPTIONS preflight from the exact production origin to `/contact`;
   expect an allowed-origin header.
5. Submit **one** controlled browser form test and verify inbox arrival if
   needed; do not repeat sends unnecessarily because rate limiting applies.

## Security and remaining work

The service validates fields, enforces TLS for SMTP, checks a honeypot, and
has a limited, per-worker rate limiter. Add edge WAF/rate limiting before
high traffic. The app does not store inquiries in a database. Keep secrets out
of issues, screenshots, logs, commits, and the frontend. Before promoting
this branch, compare it to the running app: source files were reconstructed
from the troubleshooting transcript, not pulled directly from the hosting
filesystem. Do not overwrite a working deployment without verification.
