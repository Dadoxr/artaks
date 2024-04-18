from __future__ import absolute_import, unicode_literals #Это решение проблемы циклического импорта, мы лезем в settings.py из этого файла, а сам settings.py в свою очередь тоже имеет настройки celery, поэтому может быть циклический импорт.Для этого используется absolute_import `unicode_literals используется для корректной обработки символов в юникоде`
import os, logging
from celery import Celery
from celery.signals import setup_logging
from logging.config import dictConfig
from django.conf import settings

logger = logging.getLogger(__name__)

# Установка переменной окружения для настроек проекта
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Создание экземпляра объекта Celery
app = Celery('config')
app.conf.enable_utc = False

# Загрузка настроек из файла Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение и регистрация задач из файлов tasks.py в приложениях Django
app.autodiscover_tasks()

@setup_logging.connect
def config_loggers(*args, **kwargs) -> None:
    dictConfig(settings.LOGGING)


