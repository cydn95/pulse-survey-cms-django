import os  # isort:skip
import datetime
import environ
from django.conf.locale.en import formats as en_formats

en_formats.DATETIME_FORMAT = "F j, Y, H:i:s A"

env = environ.Env(
    #set casting, default value
    DEBUG = (bool, False)
)

# reading .env file
environ.Env.read_env()

gettext = lambda s: s
DATA_DIR = os.path.dirname(os.path.dirname(__file__))
"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 1.11.25.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'oyxb8b(f@r*7bj6+3of@-(8y^lm-o#_e)umxq2)^1#275=!m8*'
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
DEBUG = env('DEBUG')

# ALLOWED_HOSTS = ['localhost', '127.0.0.1', '13.211.252.207', 'pulse.projectai.com']
ALLOWED_HOSTS = env('DJANGO_ALLOWED_HOSTS').split(" ")

# Application definition
ROOT_URLCONF = 'mysite.urls'

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/
# LANGUAGE_CODE = 'en'
LANGUAGE_CODE = env("LANGUAGE_CODE")

# TIME_ZONE = 'Australia/Perth'
TIME_ZONE = env("TIME_ZONE")

USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(DATA_DIR, 'media')
STATIC_ROOT = os.path.join(DATA_DIR, 'static')

STATICFILES_DIRS = (
    # os.path.join(BASE_DIR, 'mysite', 'static'),
    os.path.join(BASE_DIR, 'mysite', 'static'),
)

# 1: local 2: prod mode
SITE_ID = 2
# SITE_URL = 'http://13.211.252.207:3031'
SITE_URL = env("SITE_URL")

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'mysite', 'templates'),],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.template.context_processors.csrf',
                'django.template.context_processors.tz',
                'sekizai.context_processors.sekizai',
                'django.template.context_processors.static',
                'cms.context_processors.cms_settings'
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'django.template.loaders.eggs.Loader'
            ],
        },
    },
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'cms.middleware.utils.ApphookReloadMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
    'preventconcurrentlogins.middleware.PreventConcurrentLoginsMiddleware',
]

INSTALLED_APPS = [
    'jet',
    'jet.dashboard',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'cms',
    'menus',
    'sekizai',
    'treebeard',
    'djangocms_text_ckeditor',
    'filer',
    'boolean_switch',
    'easy_thumbnails',
    'tabbed_admin',
    'inline_actions',
    'djangocms_column',
    'djangocms_file',
    'djangocms_link',
    'djangocms_picture',
    'djangocms_style',
    'djangocms_snippet',
    'djangocms_googlemap',
    'djangocms_video',
    'tinymce',
    'colorfield',
    'filebrowser',
    'mysite',
    'organization',
    'team',
    'survey',
    'shgroup',
    'setting',
    'aboutme',
    'aboutothers',
    'page_nav',
    'page_setting',
    'option',
    'journey',
    'adminsortable2',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_auth.registration',
    'corsheaders',
    'snippets.apps.SnippetsConfig',
    'import_export',
    'django_filters',
    'rest_framework_swagger',
    'django_inlinecss',
    'django_rest_passwordreset',
    'preventconcurrentlogins',
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    }
]

LANGUAGES = (
    ## Customize this
    ('en', gettext('en')),
)

CMS_LANGUAGES = {
    ## Customize this
    1: [
        {
            'code': 'en',
            'name': gettext('en'),
            'redirect_on_fallback': True,
            'public': True,
            'hide_untranslated': False,
        },
    ],
    'default': {
        'redirect_on_fallback': True,
        'public': True,
        'hide_untranslated': False,
    },
}

CMS_TEMPLATES = (
    ## Customize this
    ('fullwidth.html', 'Fullwidth'),
    ('sidebar_left.html', 'Sidebar Left'),
    ('sidebar_right.html', 'Sidebar Right')
)

CMS_PERMISSION = True

CMS_PLACEHOLDER_CONF = {}
DATABASES = {
    'default': {
        'ENGINE': env("SQL_ENGINE"),
        'NAME': env("SQL_DATABASE"),
        'USER': env("SQL_USER"),
        'PASSWORD': env("SQL_PASSWORD"),
        'HOST': env("SQL_HOST"),
        'PORT':env("SQL_PORT"),
    }
}

MIGRATION_MODULES = {
    
}

TABBED_ADMIN_USE_JQUERY_UI = True

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters'
)

# default, green, light-violet, light-green, light-blue, light-gray
JET_DEFAULT_THEME = 'default'

JET_THEMES = [
    {
        'theme': 'default', # theme folder name
        'color': '#47bac1', # color of the theme's button in user menu
        'title': 'Default'  # theme title
    },
    {
        'theme': 'green',
        'color': '#44b78b',
        'title': 'Green'
    },
    {
        'theme': 'light-green',
        'color': '#2faa60',
        'title': 'Light Green'
    },
    {
        'theme': 'light-violet',
        'color': '#a464c4',
        'title': 'Light Violet'
    },
    {
        'theme': 'light-blue',
        'color': '#5EADDE',
        'title': 'Light Blue'
    },
    {
        'theme': 'light-gray',
        'color': '#222',
        'title': 'Light Gray'
    }
]

JET_SIDE_MENU_COMPACT = False
JET_CHANGE_FORM_SIBLING_LINKS = False

JET_SIDE_MENU_ITEMS = [ # A list of application or custom item dicts
    # {'label': 'All Pages', 'items': [
    #     {'name': 'cms.page', 'label': 'Pages'},
    #     {'name': 'page_setting.pagesetting', 'label': 'Set Page Contents'},
    #     {'name': 'page_nav.pagenav', 'label': 'Set Page Order'},
    # ]},
    {'label': 'Users', 'items': [
        #{'name': 'auth.group'},
        {'name': 'auth.user'},
        {'name': 'journey.journey', 'label': 'User Journey'},
    ]},
    {'label': 'About Me Questions', 'items': [
        {'name': 'aboutme.amquestion', 'label': 'Questions'},
        {'name': 'aboutme.amresponse', 'label': 'Responses'},
    ]},
    {'label': 'About Other Questions', 'items': [
        {'name': 'aboutothers.aoquestion', 'label': 'Questions'},
        {'name': 'aboutothers.aoresponse', 'label': 'Responses'},
    ]},
    {'label': 'StakeHolders', 'items': [
        {'name':'shgroup.shcategory', 'label': 'Categories'},
        {'name':'shgroup.shgroup', 'label': 'Groups'},
        {'name':'survey.project', 'label': 'Projects'},
        {'name':'survey.driver', 'label': 'Drivers'},
        {'name':'shgroup.projectuser', 'label': 'Project Users'},
        {'name':'team.team', 'label': 'Project Teams'},
        {'name':'shgroup.shmapping', 'label': 'SHMapping'},
        {'name':'survey.configpage', 'label': 'Pages'},
        {'name':'survey.nikelmobilepage', 'label': 'Nikel Tower(for mobile)'},
        {'name':'survey.tooltipguide', 'label': 'Tooltip'},
    ]},
    {'label': 'Configuration', 'items': [
        {'name':'survey.survey', 'label': 'Configurations'}
    ]}
]

APPEND_SLASH = True

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'drf_renderer_xlsx.renderers.XLSXRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': None,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema'
}

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CSRF_COOKIE_NAME = "csrftoken"

JWT_AUTH = {
    'JWT_ENCODE_HANDLER':
    'rest_framework_jwt.utils.jwt_encode_handler',

    'JWT_DECODE_HANDLER':
    'rest_framework_jwt.utils.jwt_decode_handler',

    'JWT_PAYLOAD_HANDLER':
    'rest_framework_jwt.utils.jwt_payload_handler',

    'JWT_PAYLOAD_GET_USER_ID_HANDLER':
    'rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler',

    'JWT_RESPONSE_PAYLOAD_HANDLER':
    'rest_framework_jwt.utils.jwt_response_payload_handler',

    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_GET_USER_SECRET_KEY': None,
    'JWT_PUBLIC_KEY': None,
    'JWT_PRIVATE_KEY': None,
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LEEWAY': 0,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(minutes=60),
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': None,

    'JWT_ALLOW_REFRESH': False,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=7),

    'JWT_AUTH_HEADER_PREFIX': 'JWT',
    'JWT_AUTH_COOKIE': None,
}

TINYMCE_JS_URL = os.path.join(STATIC_URL, "js/tinymce/tinymce.min.js")
TINYMCE_JS_ROOT = os.path.join(STATIC_URL, "js/tinymce")

TINYMCE_DEFAULT_CONFIG = {
    'height': 300,
    'plugins': "image, imagetools, media, codesample, link, code",
    'cleanup_on_startup': True,
    'menubar': False,
    'toolbar': "styleselect | undo redo | bold italic | alignleft aligncenter alignright | link image media codesample code",
    'image_caption': True,
    'image_advtab': True,
    'custom_undo_redo_levels': 10,
}

DATA_UPLOAD_MAX_MEMORY_SIZE = 100000000
DATA_UPLOAD_MAX_NUMBER_FIELDS = 102400 # higher than the count of fields

CORS_ORIGIN_WHITELIST = [
    'http://localhost:3000',
    'http://localhost:3001',
    'http://13.211.252.207:3000',
    'http://13.211.252.207:3001',
    'http://13.211.252.207',
]

# For sendgrid mail
# SENDGRID_API_KEY = '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'   # for send grid
# EMAIL_HOST = 'smtp.sendgrid.net'   # for send grid

# EMAIL_HOST_USER = 'pulseprojectai'
# EMAIL_HOST_USER = 'apikey'    # for send grid
# EMAIL_HOST_PASSWORD = 'RocketMan39'
# EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'pulse@projectai.com'
# DEFAULT_FROM_EMAIL = 'jaclindev99@gmail.com'
# ACCOUNT_EMAIL_SUBJECT_PREFIX = 'Contact email received from website'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'       # for send grid

EMAIL_BACKEND = 'django_ses.SESBackend'

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'jaclindev99@gmail.com'
# EMAIL_HOST_PASSWORD = 'zvujltulyzihnauy'

# AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_ACCESS_KEY_ID = 'AKIASKYV22E36XZSVO2X'
AWS_SECRET_ACCESS_KEY = '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'
AWS_SES_REGION_NAME = 'ap-southeast-2'
AWS_SES_REGION_ENDPOINT = 'email.ap-southeast-2.amazonaws.com'

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of 'allauth'
    # "django.contrib.auth.backends.ModelBackend",

    # 'allauth' specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
)

ACCOUNT_USER_MODEL_USERNAME_FIELD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_UNIQUE_USERNAME = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'email'

ACCOUNT_ADAPTER = 'mysite.account_adapter.AccountAdapter'

ACCOUNT_UNIQUE_EMAIL = True
SOCIALACCOUNT_AUTO_SIGNUP = False
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300
