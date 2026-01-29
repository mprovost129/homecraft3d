from django_ratelimit.decorators import ratelimit
from django.conf import settings


# Example: Rate limit login attempts to 5 per minute per IP
LOGIN_RATELIMIT = '5/m'
# Rate limit registration attempts to 3 per minute per IP
REGISTER_RATELIMIT = '3/m'
# Rate limit password reset requests to 3 per minute per IP
PASSWORD_RESET_RATELIMIT = '3/m'
