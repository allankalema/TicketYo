import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-xrsoe(-i(#r!obcems%2nmc1j3jn=tmck59wq0lvcw+3_g$fx$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'jazzmin',  # Jazzmin for custom admin interface
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'customers',
    'vendors',
    'events',
    'tickets',
    'payments',
    'notifications',
    'analytics',
    'api',
    'frontend',
    'pos',
    'accounts',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'django.contrib.humanize',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    
]

ROOT_URLCONF = 'TicketYo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Specify templates directory
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

WSGI_APPLICATION = 'TicketYo.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Language and time zone
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Custom authentication backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]



SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}


SOCIALACCOUNT_LOGIN_ON_GET = True

LOGIN_REDIRECT_URL = '/events/home/'


LOGOUT_REDIRECT_URL = '/Accounts/login'

## Jazzmin settings for customizing the admin interface
JAZZMIN_SETTINGS = {
    "site_title": "TicketYo Admin",
    "site_header": "TicketYo Admin Panel",
    "custom_css": "css/admin.css",
    "welcome_sign": "Welcome to TicketYo's Admin Dashboard 😊",
    "site_logo": "frontend/logo.jpg",  # Correct path to your logo in the static folder
    "login_logo": "frontend/logo.jpg",  # Logo on the login page
    "login_logo_dark": "frontend/logo.jpg",  # Dark version of the logo on the login page
    "site_brand": "TicketYo",  # Brand name shown on the sidebar
    "show_sidebar": True,  # Display the sidebar
    "navigation_expanded": True,  # Expand navigation menu by default
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
    ],
    "user_avatar": None,  # Option to use an avatar field for users
}


# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'ticketyotechnologies@gmail.com'
EMAIL_HOST_PASSWORD = 'sldd pbjt smoa tzod'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# LOGIN URL
LOGIN_URL = '/Accounts/login/'  # Update to the correct path if needed

SITE_URL = 'http://127.0.0.1:8000/'

SOCIALACCOUNT_ADAPTER = 'accounts.addapters.MySocialAccountAdapter'


BLINK_API_URL = config('BLINK_API_URL')
BLINK_API_USERNAME = config('BLINK_API_USERNAME')
BLINK_API_PASSWORD = config('BLINK_API_PASSWORD')
BLINK_STATUS_NOTIFICATION_URL = config('BLINK_STATUS_NOTIFICATION_URL')
