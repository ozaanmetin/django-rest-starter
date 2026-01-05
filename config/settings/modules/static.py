"""
Static and media files configuration for the Django application.

@author Ozan Metin
"""

import environ
from pathlib import Path

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = env.str('MEDIA_URL', default='/media/')
MEDIA_ROOT = env.str('MEDIA_ROOT', default=BASE_DIR / 'media')
