import sys
import dotenv
import os
from pathlib import Path
from kombu import Queue
from celery.schedules import crontab


VAR_PATH = os.path.join(Path(__file__).resolve().parent.parent, 'var')
dotenv.load_dotenv(os.path.join(VAR_PATH, '.env'), override=True)

DEBUG = str(os.getenv('DEBUG')) == 'True'

SECRET_KEY = str(os.getenv('DJANGO_SECRET_KEY'))

BASE_DIR = Path(__file__).resolve().parent.parent


ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',
    'contact',
    'crispy_forms',
	'crispy_bootstrap5',
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


ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'


DATABASES = {
	'default': {
		'ENGINE': str(os.getenv('POSTGRES_ENGINE')),
		'NAME': str(os.getenv('POSTGRES_DB')),
		'USER': str(os.getenv('POSTGRES_USER')),
		'PASSWORD': str(os.getenv('POSTGRES_PASSWORD')),
		'HOST': str(os.getenv('POSTGRES_HOST')),
		'PORT': str(os.getenv('POSTGRES_PORT')),
		'ATOMIC_REQUESTS': True
	}
}



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


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATIC_URL = '/static/'
if DEBUG:
    STATICFILES_DIRS = [BASE_DIR / 'static']
else:
    STATIC_ROOT = BASE_DIR / 'static'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"


CELERY_CACHE_BACKEND = 'default'
CELERY_BROKER_URL = f'redis://{str(os.getenv("REDIS_HOST"))}:{str(os.getenv("REDIS_PORT"))}/0' 
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_TASK_TRACK_STARTED = True 
CELERY_RESULT_SERIALIZER = 'json'
CELERYD_HIJACK_ROOT_LOGGER = False
CELERY_IGNORE_RESULT = True
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_RESULT_BACKEND = 'django-db'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_ENABLE_UTC=False
CELERY_BEAT_SCHEDULE = {
    'task_renew_contact': {
        'task': 'contact.tasks.task_renew_contact',
        'schedule': crontab(hour='0'),
    },
}

CELERY_TASK_QUEUES = (
    Queue('tasks', routing_key='tasks.#'),
)
CELERY_TASK_DEFAULT_QUEUE = 'other'
CELERY_TASK_DEFAULT_EXCHANGE = 'other'
CELERY_TASK_DEFAULT_ROUTING_KEY = 'other.default'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout
        }
    },
    'loggers': {
        logger_name: {
            'handlers': ['console'],
            'propagate': False,
            'level': 'WARNING'
        } for logger_name in ('django', 'django_request', 'django.db.backends', 'django.template', 'core')
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO'
    }
}