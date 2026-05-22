"""
Django settings for AeroMiles project (TK03).

Spec TK03 mensyaratkan TIDAK menggunakan Django ORM. Konfigurasi ini:
- Tidak memakai django.contrib.auth, admin, contenttypes (semua butuh ORM tables).
- Memakai signed-cookie session, sehingga tidak butuh django_session table.
- Akses database hanya lewat psycopg2 (lihat main/db.py).
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-dev-key-change-in-production')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']


def get_db_config():
    """Parse Neon connection string atau fallback ke variabel terpisah."""
    conn_string = os.getenv('NEON_CONNECTION_STRING', '')
    if conn_string:
        parsed = urlparse(conn_string)
        options = {'sslmode': 'require'} if parsed.query else {}
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': parsed.path.lstrip('/'),
            'USER': parsed.username,
            'PASSWORD': parsed.password,
            'HOST': parsed.hostname,
            'PORT': parsed.port or 5432,
            'OPTIONS': options,
        }
    return {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('NEON_DB_NAME', 'neondb'),
        'USER': os.getenv('NEON_DB_USER', ''),
        'PASSWORD': os.getenv('NEON_DB_PASSWORD', ''),
        'HOST': os.getenv('NEON_DB_HOST', ''),
        'PORT': os.getenv('NEON_DB_PORT', '5432'),
    }


# Catatan: konfigurasi DATABASES tetap dipertahankan supaya psycopg2 bisa membaca
# kredensial dari Django settings (lihat main/db.py: get_connection()).
# Tidak ada model yang di-manage Django — semua query pakai psycopg2 raw SQL.
DATABASES = {
    'default': get_db_config()
}

INSTALLED_APPS = [
    # Hanya app yang menyediakan template loader & static files; TIDAK termasuk
    # django.contrib.auth/admin/contenttypes karena membutuhkan tabel ORM.
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'django.contrib.sessions',
    'features.accounts',
    'features.flights',
    'features.transactions',
    'features.rewards',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'features' / 'accounts' / 'templates',
            BASE_DIR / 'features' / 'flights' / 'templates',
            BASE_DIR / 'features' / 'transactions' / 'templates',
            BASE_DIR / 'features' / 'rewards' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'main.context_processors.user_session',
            ],
        },
    },
]

WSGI_APPLICATION = 'main.wsgi.application'

# Gunakan signed-cookie session: data session disimpan di cookie ter-tanda-tangan,
# sehingga TIDAK perlu tabel django_session di database.
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

MESSAGE_TAGS = {
    'messages.SUCCESS': 'success',
    'messages.ERROR': 'error',
}
