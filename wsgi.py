"""Module used by gunicorn for starting flask app."""
import application.app

app = application.app.wsgi()
