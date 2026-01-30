
import os
from django.conf import settings

# Determine if running in development (DEBUG True or env var)
IS_DEV = getattr(settings, 'DEBUG', False) or os.environ.get('DJANGO_ENV') == 'development'

if IS_DEV:
	# Effectively disable rate limiting in development
	LOGIN_RATELIMIT = '1000/m'
	REGISTER_RATELIMIT = '1000/m'
	PASSWORD_RESET_RATELIMIT = '1000/m'
else:
	# Production limits
	LOGIN_RATELIMIT = '5/m'
	REGISTER_RATELIMIT = '3/m'
	PASSWORD_RESET_RATELIMIT = '3/m'
