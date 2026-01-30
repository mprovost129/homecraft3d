# Silence recaptcha test key warning in development
SILENCED_SYSTEM_CHECKS = ['django_recaptcha.recaptcha_test_key_error']
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'homecraft3d.onrender.com', 'www.homecraft3d.com', 'homecraft3d.com']

# Local development database settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }
}

# Ensure reCAPTCHA default action matches form usage
RECAPTCHA_DEFAULT_ACTION = 'register'


