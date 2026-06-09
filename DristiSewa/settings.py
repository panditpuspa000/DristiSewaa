import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / 'apps'))

# ================= SECURITY =================
SECRET_KEY = 'django-insecure-(uw(cwz(j=h(%&vy1lu3=oge-e&_=nx(h+al@sfr(=&@da&g^-)'
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'localhost:8000']


# ================= INSTALLED APPS =================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'frontdesk_core',

    # Custom Apps
    'apps.accounts',          # 🔐 CRITICAL: Kept at the top so AUTH_USER_MODEL loads first
    'apps.notifications',
    'students_app',

    # Frontdesk (future)
    # 'apps.frontdesk_core',
]


# ================= MIDDLEWARE =================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ================= ROOT URL =================
ROOT_URLCONF = 'DristiSewa.urls'
WSGI_APPLICATION = 'DristiSewa.wsgi.application'


# ================= TEMPLATES (IMPORTANT FIX FOR ADMIN.E403) =================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # 🔥 REQUIRED for admin
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ================= DATABASE =================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ================= AUTH =================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'accounts.User'


# ================= INTERNATIONAL =================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kathmandu'
USE_I18N = True
USE_TZ = True


# ================= STATIC / MEDIA =================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ================= DEFAULT =================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ================= LOGIN =================
LOGIN_URL = 'accounts:staff_login'
LOGIN_REDIRECT_URL = 'accounts:admin_dashboard'
LOGOUT_REDIRECT_URL = 'accounts:staff_login'


# ================= CSRF (DEV ONLY) =================
if DEBUG:
    CSRF_TRUSTED_ORIGINS = [
        'http://127.0.0.1:8000',
        'http://localhost:8000',
    ]

    CSRF_COOKIE_PATH = '/'
    SESSION_COOKIE_PATH = '/'

    CSRF_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SAMESITE = 'Lax'

    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False


# ================= EMAIL =================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = 'panditpuspa000@gmail.com'
EMAIL_HOST_PASSWORD = 'rpnandvoiairdgym'
DEFAULT_FROM_EMAIL = f"DristiSewa Platform <{EMAIL_HOST_USER}>"