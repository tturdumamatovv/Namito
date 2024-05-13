# ruff: noqa: ERA001, E501
"""Base settings to build other settings files upon."""

from pathlib import Path
from decouple import config
from datetime import timedelta

import os
import environ

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
# namito/
APPS_DIR = BASE_DIR / "namito"
env = environ.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(BASE_DIR / ".env"))

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", False)
PRODUCTION = True
# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = "UTC"
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "ru"
# https://docs.djangoproject.com/en/dev/ref/settings/#languages
from django.utils.translation import gettext_lazy as _
LANGUAGES = [
    ('en', _('English')),
    ('ru', _('Russian')),
]
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
# https://docs.djangoproject.com/en/dev/ref/settings/#locale-paths
LOCALE_PATHS = [str(BASE_DIR / "locale")]

# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# DATABASES["default"]["ATOMIC_REQUESTS"] = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', cast=int),
    }
}
# https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-DEFAULT_AUTO_FIELD
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "simpleui",
    'modeltranslation',
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # "django.contrib.humanize", # Handy template tags
    "django.contrib.admin",
    "django.forms",
]
THIRD_PARTY_APPS = [
    "crispy_forms",
    "crispy_bootstrap5",
    "allauth",
    "allauth.account",
    # "allauth.mfa",
    'nested_admin',
    "allauth.socialaccount",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "drf_spectacular",
    'mptt',
    'drf_yasg',
    'django_filters',

]

LOCAL_APPS = [
    "namito.users",
    "namito.catalog",
    "namito.orders",
    "namito.advertisement",
    "namito.pages"
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIGRATIONS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules
MIGRATION_MODULES = {"sites": "namito.contrib.sites.migrations"}

# AUTHENTICATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = "users.User"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url
LOGIN_REDIRECT_URL = "users:redirect"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = "account_login"

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    'namito.pages.middleware.LanguageMiddleware',

    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
# STATIC_ROOT = str(BASE_DIR / "static")
# # https://docs.djangoproject.com/en/dev/ref/settings/#static-url
# STATIC_URL = "/static/"
# # https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'assets'),
]
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')


# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#dirs
        "DIRS": [str(APPS_DIR / "templates")],
        # https://docs.djangoproject.com/en/dev/ref/settings/#app-dirs
        "APP_DIRS": True,
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "namito.users.context_processors.allauth_settings",
            ],
        },
    },
]

# https://docs.djangoproject.com/en/dev/ref/settings/#form-renderer
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = "bootstrap5"
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

# FIXTURES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#fixture-dirs
FIXTURE_DIRS = (str(APPS_DIR / "fixtures"),)

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options
X_FRAME_OPTIONS = "DENY"

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#email-timeout
EMAIL_TIMEOUT = 5

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = "admin/"
# https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [("""Daniel Roy Greenfeld""", "daniel-roy-greenfeld@example.com")]
# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS
# https://cookiecutter-django.readthedocs.io/en/latest/settings.html#other-environment-settings
# Force the `admin` sign in process to go through the `django-allauth` workflow
DJANGO_ADMIN_FORCE_ALLAUTH = env.bool("DJANGO_ADMIN_FORCE_ALLAUTH", default=False)

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"level": "INFO", "handlers": ["console"]},
}

CSRF_TRUSTED_ORIGINS = ['https://namito.tatadev.pro/', 'https://www.namito.tatadev.pro/']

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# django-allauth
# ------------------------------------------------------------------------------
ACCOUNT_ALLOW_REGISTRATION = env.bool("DJANGO_ACCOUNT_ALLOW_REGISTRATION", True)
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_AUTHENTICATION_METHOD = "username"
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_EMAIL_REQUIRED = True
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_ADAPTER = "namito.users.adapters.AccountAdapter"
# https://docs.allauth.org/en/latest/account/forms.html
ACCOUNT_FORMS = {"signup": "namito.users.forms.UserSignupForm"}
# https://docs.allauth.org/en/latest/socialaccount/configuration.html
SOCIALACCOUNT_ADAPTER = "namito.users.adapters.SocialAccountAdapter"
# https://docs.allauth.org/en/latest/socialaccount/configuration.html
SOCIALACCOUNT_FORMS = {"signup": "namito.users.forms.UserSocialSignupForm"}

# django-rest-framework
# -------------------------------------------------------------------------------
# django-rest-framework - https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
}

DEFAULT_PROFILE_PICTURE_URL = "https://static.vecteezy.com/system/resources/thumbnails/009/292/244/small/default-avatar-icon-of-social-media-user-vector.jpg"

DEFAULT_PRODUCT_URL = "data:image/png;base64,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"

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=14),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
}

# django-cors-headers - https://github.com/adamchainz/django-cors-headers#setup
CORS_URLS_REGEX = r"^/api/.*$"

# By Default swagger ui is available only to admin user(s). You can change permission classes to change that
# See more configuration options at https://drf-spectacular.readthedocs.io/en/latest/settings.html#settings
SPECTACULAR_SETTINGS = {
    "TITLE": "Namito API",
    "DESCRIPTION": "Documentation of API endpoints of Namito",
    "VERSION": "1.0.0",
    "SERVE_PERMISSIONS": ["rest_framework.permissions.IsAdminUser"],
}
# Your stuff...
# ------------------------------------------------------------------------
SIMPLEUI_ICON = {
    "Catalog": "fa fa-shopping-bag",
    "Categories": "fa fa-book",
    "Products": "fa fa-cube",
    "Variants": "fa fa-cubes",

}

SIMPLEUI_HOME_INFO = False
SIMPLEUI_HOME_ACTION = False
SIMPLEUI_HOME_QUICK = True
SIMPLEUI_INDEX = '#'

SIMPLEUI_CONFIG = {
    'system_keep': False,
    'menus': [
        {
            'name': 'Catalog',
            'icon': 'fa fa-book',
            'models': [
                {
                    'name': 'Categories',
                    'icon': 'fa fa-list',
                    'url': '/admin/catalog/category/'
                },
                {
                    'name': 'Brands',
                    'icon': 'fa fa-money-bill',
                    'url': '/admin/catalog/brand/'
                },
                {
                    'name': 'Products',
                    'icon': 'fa fa-cube',
                    'url': '/admin/catalog/product/'
                },

                # {
                #     'name': 'Images',
                #     'icon': 'fa fa-image',
                #     'url': '/admin/catalog/image/'
                # },
                {
                    'name': 'Configurations',
                    'models': [
                        {
                            'name': 'Sizes',
                            'icon': 'fa fa-ruler',
                            'url': '/admin/catalog/size/'
                        },
                        {
                            'name': 'Colors',
                            'icon': 'fa fa-circle',
                            'url': '/admin/catalog/color/'
                        },
                        {
                            'name': 'Tags',
                            'icon': 'fa fa-tag',
                            'url': '/admin/catalog/tag/'
                        },
                        {
                            'name': 'Size Chart',
                            'icon': 'fa fa-table',
                            'url': '/admin/catalog/sizechart/'
                        },
                    ]
                },
            ]
        },
        {
            'name': 'Users',
            'icon': 'fa fa-user',
            'models': [
                {
                    'name': 'Users',
                    'icon': 'fa fa-user',
                    'url': '/admin/users/user/'
                },
                {
                    'name': 'Carts',
                    'icon': 'fa fa-shopping-cart',
                    'url': '/admin/orders/cart/'
                },

            ]
        },
        {
            'name': 'Orders',
            'icon': 'fa fa-star',
            'url': '/admin/orders/order/'
        },
        {
            'name': 'Главная страница',
            'icon': 'fa fa-window-maximize',
            'url': '/admin/pages/mainpage/'
        },
        {
            'name': 'Static Pages',
            'icon': 'fa fa-file-text',
            'url': '/admin/pages/staticpage/'
        },
    ]
}
