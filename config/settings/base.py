import environ
from pathlib import Path
import os

BASE_DIR = 'C:\\Users\\mprov\\Dropbox\\Projects\\home_craft_3d\\3dprint_marketplace'


# Initialise environment variables
env = environ.Env(
    DJANGO_DEBUG=(bool, True)
)
env_path = Path(BASE_DIR) / '.env'
print(f"[DEBUG] Reading .env from: {env_path}")
environ.Env.read_env(env_path)

SECRET_KEY = env('DJANGO_SECRET_KEY')
DEBUG = env('DJANGO_DEBUG')
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
if 'homecraft3d.onrender.com' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('homecraft3d.onrender.com')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 2FA and OTP
    'django_otp',
    'django_otp.plugins.otp_totp',
    'two_factor',
    # Project apps
    'accounts',
    'storefront',
    'products',
    'orders',
    'sellers',
    'payments',
    'moderation',
    'reviews',
    'legal',
    'messaging',
    'django_recaptcha',
]

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [Path(BASE_DIR) / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'config.store_context.store_name',
                'storefront.context_processors.cart_item_count',
                'storefront.context_processors.theme_mode',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Static & Media
STATIC_URL = '/static/'
STATICFILES_DIRS = [Path(BASE_DIR) / 'static']
STATIC_ROOT = Path(BASE_DIR) / 'staticfiles'
MEDIA_URL = '/media/'

MEDIA_ROOT = Path(BASE_DIR) / 'media'
# SECURITY: Ensure the media directory is not web-accessible in production (serve via a secure method, not directly by web server)
# Set restrictive permissions on the media directory (e.g., 750 or 700) and never allow execution (no +x on files)


# --- Security Headers ---
# Prevent clickjacking
X_FRAME_OPTIONS = 'DENY'
# Prevent content sniffing
SECURE_CONTENT_TYPE_NOSNIFF = True
# XSS protection (modern browsers ignore, but safe to set)
SECURE_BROWSER_XSS_FILTER = True
# Referrer policy
SECURE_REFERRER_POLICY = 'same-origin'
# HSTS (enable in production only)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CSP (Content Security Policy) - adjust as needed for your frontend
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", 'https://www.google.com/recaptcha/', 'https://www.gstatic.com/recaptcha/')
CSP_STYLE_SRC = ("'self'", 'https://fonts.googleapis.com')
CSP_FONT_SRC = ("'self'", 'https://fonts.gstatic.com')
CSP_IMG_SRC = ("'self'", 'data:')
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_SRC = ("'self'", 'https://www.google.com/recaptcha/')

# --- Session & Cookie Security ---
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
SECURE_SSL_REDIRECT = not DEBUG  # Only redirect to HTTPS in production


# --- Logging ---
from config.logging_settings import LOGGING

STORE_NAME = 'Home Craft 3d'

# Stripe API keys (set your sandbox keys in .env)
STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY')

# Add your reCAPTCHA v3 keys here
RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')
RECAPTCHA_DEFAULT_ACTION = 'generic'
RECAPTCHA_SCORE_THRESHOLD = 0.5


# Email backend (development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@3dprintmarketplace.local'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Email verification for new accounts and password resets
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  # For django-allauth, if used
ACCOUNT_EMAIL_REQUIRED = True

# If not using allauth, use Django's built-in email confirmation for password reset
# For registration, send a confirmation email manually in your registration view
# Example: after user creation, send a confirmation email with a token link
# You can use django.core.mail.send_mail or Django's PasswordResetTokenGenerator
