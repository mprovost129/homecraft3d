from .base import *


DEBUG = True
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')

# Render production database settings (use environment variables provided by Render)
DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=IS_RENDER,  # SSL on Render; allow non-SSL locally if you ever set DATABASE_URL locally
        )
    }