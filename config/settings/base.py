# config/settings/base.py

import os
from pathlib import Path

import environ
import dj_database_url

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------
# NOTE: your original BASE_DIR was a string; use a real Path.
# This matches your project layout where base.py is in config/settings/.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ------------------------------------------------------------
# Environment
# ------------------------------------------------------------
env = environ.Env(
    DJANGO_DEBUG=(bool, True),
)

# Read .env from project root (BASE_DIR/.env)
env_path = BASE_DIR / ".env"
print(f"[DEBUG] Reading .env from: {env_path}")
if env_path.exists():
    environ.Env.read_env(env_path)

# ------------------------------------------------------------
# Core settings
# ------------------------------------------------------------
SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DJANGO_DEBUG")

# Render sets RENDER=true automatically on the service runtime
IS_RENDER = os.environ.get("RENDER") == "true"

# Allowed hosts
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if h.strip()]
if "homecraft3d.onrender.com" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append("homecraft3d.onrender.com")

# ------------------------------------------------------------
# Apps
# ------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 2FA and OTP
    "django_otp",
    "django_otp.plugins.otp_totp",
    "two_factor",
    # Project apps
    "accounts.apps.AccountsConfig",
    "storefront",
    "products",
    "orders",
    "sellers",
    "payments",
    "moderation",
    "reviews",
    "legal",
    "messaging",
    "django_recaptcha",
]

AUTH_USER_MODEL = "accounts.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "config.store_context.store_name",
                "storefront.context_processors.cart_item_count",
                "storefront.context_processors.theme_mode",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ------------------------------------------------------------
# Database
# ------------------------------------------------------------
# Render: use DATABASE_URL (managed Postgres)
# Local: use DB_* from .env (your existing local Postgres config)
# If you want SQLite locally, you can remove the local Postgres block and keep the SQLite fallback.
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

if DATABASE_URL:
    # Production/Render path (or any environment providing DATABASE_URL)
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=IS_RENDER,  # SSL on Render; allow non-SSL locally if you ever set DATABASE_URL locally
        )
    }
else:
    if IS_RENDER:
        # Hard fail on Render if DATABASE_URL isn't injected
        raise RuntimeError(
            "DATABASE_URL is not set on Render. "
            "In Render: Web Service → Environment → Add from Database."
        )

    # Local development Postgres via .env variables (your original local DB config)
    # Requires these in .env: DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
    db_name = env("DB_NAME")
    db_user = env("DB_USER")
    db_password = env("DB_PASSWORD")
    db_host = env("DB_HOST")
    db_port = env("DB_PORT")

    if all([db_name, db_user, db_password, db_host, db_port]):
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": db_name,
                "USER": db_user,
                "PASSWORD": db_password,
                "HOST": db_host,
                "PORT": db_port,
            }
        }
    else:
        # Local fallback: SQLite (prevents your makemigrations from crashing)
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        }

# ------------------------------------------------------------
# Static & Media
# ------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ------------------------------------------------------------
# Security Headers
# ------------------------------------------------------------
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = "same-origin"

# HSTS (enable in production only)
# Only turn HSTS on when DEBUG is False, otherwise local dev gets annoying.
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CSP (only effective if you have django-csp installed and middleware configured)
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "https://www.google.com/recaptcha/", "https://www.gstatic.com/recaptcha/")
CSP_STYLE_SRC = ("'self'", "https://fonts.googleapis.com")
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
CSP_IMG_SRC = ("'self'", "data:")
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_SRC = ("'self'", "https://www.google.com/recaptcha/")

# ------------------------------------------------------------
# Session & Cookie Security
# ------------------------------------------------------------
# Only force secure cookies/redirects when not DEBUG.
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"

SECURE_SSL_REDIRECT = not DEBUG

# ------------------------------------------------------------
# Logging
# ------------------------------------------------------------
from config.logging_settings import LOGGING  # noqa: E402

# ------------------------------------------------------------
# Store
# ------------------------------------------------------------
STORE_NAME = "Home Craft 3d"

# ------------------------------------------------------------
# Stripe
# ------------------------------------------------------------
STRIPE_PUBLIC_KEY = env("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY")

# ------------------------------------------------------------
# reCAPTCHA
# ------------------------------------------------------------
RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = os.environ.get("RECAPTCHA_PRIVATE_KEY")
RECAPTCHA_SCORE_THRESHOLD = 0.5

# ------------------------------------------------------------
# Email (development)
# ------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@3dprintmarketplace.local"

# ------------------------------------------------------------
# Password validation
# ------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ------------------------------------------------------------
# Account / Email verification (note: only applies if you're using allauth)
# ------------------------------------------------------------
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_REQUIRED = True
