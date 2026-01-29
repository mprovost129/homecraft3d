
import logging
import os
from config.settings.base import BASE_DIR

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django.security': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'security': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
