# 786 Solution contact form deployment

This commit adds a **separate** FastAPI contact application in `backend/contact_api` and frontend integration.

Not deployed. The browser form intentionally shows a direct email option until the real HTTPS API is configured.

1. Create a **new**, isolated Spaceship cPanel Python App. Do not edit the KHAN Trading application or reuse its files or interpreter environment.
2. Deploy `backend/contact_api` to a directory outside the website public root. Choose Python 3.12 or compatible, startup file `passenger_wsgi.py`, and entry point `application`. Install `requirements.txt` in this app environment.
3. Set `SMTP_HOST`, `SMTP_PORT`, `SMTP_SECURITY` (ssl or starttls), `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM`, `CONTACT_TO`, and `CONTACT_ALLOWED_ORIGINS` in cPanel, not in GitHub. `SMTP_FROM` must be authorized by the SMTP provider.
4. Restart the new Python application. Confirm its full URL for `/health` responds with `{"status":"ok"}`.
5. Set the exact HTTPS `data-api-url` in `timer-html-master/contact.html` to the exposed endpoint, including any application mount prefix, **after** you know the real address. Add the preview domain to CORS only when testing it.
6. Confirm a test message is received in the inbox. Do not claim delivery until it is actually received.

Security: The service validates input, enforces SMTP TLS, uses a honeypot, and provides limited per-process throttling. Add CDN/WAF rate limiting and stronger bot protection before exposing it to wide public traffic. The application does not save submissions to a database. Do not include customer private information in public repository logs.

For local tests install `fastapi`, `email-validator`, `httpx`, `pytest`, then test with mocked SMTP; real delivery remains an integration check.
