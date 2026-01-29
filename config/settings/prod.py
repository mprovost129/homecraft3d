from .base import *


DEBUG = False
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')

# Render production database settings (use environment variables provided by Render)
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': os.environ.get('DB_NAME'),
		'USER': os.environ.get('DB_USER'),
		'PASSWORD': os.environ.get('DB_PASSWORD'),
		'HOST': os.environ.get('DB_HOST'),
		'PORT': os.environ.get('DB_PORT'),
	}
}
