from pathlib import Path

# -------------------
# BASE DIR
# -------------------
BASE_DIR = Path(__file__).resolve().parent.parent


# -------------------
# SECURITY
# -------------------
SECRET_KEY = 'django-insecure-change-this-in-production'

DEBUG = True

ALLOWED_HOSTS = []


# -------------------
# APPLICATIONS
# -------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # ✅ IMPORTANT (for signals)
    'website.apps.YourAppConfig',
]


# -------------------
# MIDDLEWARE
# -------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# -------------------
# URLS
# -------------------
ROOT_URLCONF = 'ulendo.urls'


# -------------------
# TEMPLATES
# -------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        # ✅ Correct template path
        'DIRS': [BASE_DIR / "website/templates"],

        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# -------------------
# WSGI
# -------------------
WSGI_APPLICATION = 'ulendo.wsgi.application'


# -------------------
# DATABASE
# -------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# -------------------
# PASSWORD VALIDATION
# -------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# -------------------
# INTERNATIONALIZATION
# -------------------
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True
USE_TZ = True


# -------------------
# STATIC FILES
# -------------------
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "website/static",
]


# -------------------
# DEFAULT AUTO FIELD
# -------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = 'chiumiavijay75@gmail.com'
EMAIL_HOST_PASSWORD = 'fyxuwqugjngnwsib'

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER