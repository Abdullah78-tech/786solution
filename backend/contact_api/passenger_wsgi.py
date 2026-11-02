from a2wsgi import ASGIMiddleware
from app import app

# Passenger expects a WSGI callable.
application = ASGIMiddleware(app)
