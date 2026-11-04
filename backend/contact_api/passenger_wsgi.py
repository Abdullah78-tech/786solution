"""WSGI entrypoint for LiteSpeed/CloudLinux.

Keep ASGIMiddleware initialization lazy: LiteSpeed may preload this module
before forking workers. Its asyncio background thread must start in the worker.
"""
import os
import threading
from configparser import ConfigParser
from pathlib import Path

from a2wsgi import ASGIMiddleware


def _load_private_smtp_config():
    """Load private, account-local settings; never commit smtp.ini."""
    config_file = Path.home() / ".config/786solution-contact-api/smtp.ini"
    parser = ConfigParser(interpolation=None)
    if parser.read(config_file) and parser.has_section("smtp"):
        for key in (
            "SMTP_HOST",
            "SMTP_PORT",
            "SMTP_SECURITY",
            "SMTP_USERNAME",
            "SMTP_PASSWORD",
            "SMTP_FROM",
            "CONTACT_TO",
        ):
            value = parser.get("smtp", key, fallback="")
            if value and not os.environ.get(key):
                os.environ[key] = value


_load_private_smtp_config()

# Import the ASGI app after loading configuration.
from app import app

_worker_pid = None
_worker_application = None
_init_lock = threading.Lock()


def application(environ, start_response):
    """Expose a WSGI callable, initializing the adapter in each worker PID."""
    global _worker_pid, _worker_application

    current_pid = os.getpid()
    if _worker_pid != current_pid:
        with _init_lock:
            if _worker_pid != current_pid:
                _worker_application = ASGIMiddleware(app)
                _worker_pid = current_pid

    return _worker_application(environ, start_response)
