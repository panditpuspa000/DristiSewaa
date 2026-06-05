import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-(uw(cwz(j=h(%&vy1lu3=oge-e&_=nx(h+al@sfr(=&@da&g^-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ==============================================================================
# ALLOWED HOSTS CONFIGURATION
# ==============================================================================
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'localhost:8000']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Custom Apps Core 
    'apps.accounts',        # 🔐 CRITICAL: Kept at the top so AUTH_USER_MODEL loads first
    'apps.consultancy',
    'apps.notifications',
    
    # Dedicated Isolated Front Desk App 
    'apps.frontdeskstaff',  # ✅ Placed safely below accounts core dependency
    
    # Student App Setup
    'students_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'DristiSewa.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'DristiSewa.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kathmandu'  # ✅ FIXED: Synced with your local region for correct OTP timestamps
USE_I18N = True
USE_TZ = True

# ==============================================================================
# STATIC & MEDIA FILES CONFIGURATIONS
# ==============================================================================
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ==============================================================================
# AUTHENTICATION & SECURITY SETTINGS
# ==============================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'accounts.User'

# ==============================================================================
# FIXED NAMESPACED AUTH ROUTING RULES
# ==============================================================================
LOGIN_URL = 'accounts:staff_login'
LOGOUT_REDIRECT_URL = 'accounts:staff_login'
LOGIN_REDIRECT_URL = 'accounts:admin_dashboard'

# ==============================================================================
# LOCAL DEVELOPMENT COOKIE, CROSS-PATH, AND CSRF SECURITY RECOVERY ENGINE
# ==============================================================================
if DEBUG:
    # Explicitly trust local development origins to prevent modern browser 403 blocks
    CSRF_TRUSTED_ORIGINS = [
        'http://127.0.0.1:8000',
        'http://localhost:8000',
    ]
    
    # Forces cookies to match valid scopes across all subdirectories and subpaths
    CSRF_COOKIE_PATH = '/'
    SESSION_COOKIE_PATH = '/'
    
    # Prevents modern browsers from dropping security tokens on internal root domain redirects
    CSRF_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Ensures local unencrypted HTTP development doesn't block cookie storage engines
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False

    # ==============================================================================
    # SMTP GMAIL BACKEND DISPATCH CONFIGURATION NETWORK
    # ==============================================================================
    # ✅ FIXED: Replaced 'console' with active production delivery so registration OTPs are actually sent
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = 'panditpuspa000@gmail.com'
    EMAIL_HOST_PASSWORD = 'rpnandvoiairdgym'
    DEFAULT_FROM_EMAIL = f"DristiSewa Platform <{EMAIL_HOST_USER}>"