from django.conf import settings
import requests
import logging
import pandas as pd
from django.db.models.query import QuerySet
from contact.models import Contact

logger = logging.getLogger(__name__)

def download_file(filename: str, url: str):
    """
    Скачивание файлов по ссылкам
    """
    logger.info(f'Скачиваю {filename}')
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        logger.info(f"Скачен {filename} успешно")
    else:
        logger.error(f"Ошибка скачивания {filename}: status code {response.status_code}")


def add_or_update_contacts(exists_contact_objects: QuerySet[Contact], new_contact_objects: list[Contact]):
    """
    Добавление или обновление контактов на основе списка новых контактов.
    """
    logger.info('Обновляю контакты и добавляю новые')
    
    add_list = []
    updated_contact = 0

    for new_contact in new_contact_objects: 
        exists_contact = exists_contact_objects.filter(abc=new_contact.abc, start=new_contact.start, end=new_contact.end)

        if exists_contact.count() < 2:
            if exists_contact.exists():
                nc, ec = new_contact, exists_contact.first()
                updated_fields = False

                for field in ['operator', 'region', 'territory', 'inn']:
                    if getattr(nc, field) != getattr(ec, field):
                        setattr(ec, field, getattr(nc, field))
                        updated_fields = True
                if updated_fields:
                    ec.save()
                    updated_contact += 1
            else:
                add_list.append(new_contact)
        else:
            logger.warning(f'Найден задублированный контакт: {list(exists_contact)}. Function: add_or_update_contacts')

    if add_list:
        Contact.objects.bulk_create(add_list)
    logger.info(f'{len(add_list)} контактов создано и {updated_contact} контактов обновлено')


def delete_from_db_if_not_in_new_list(exists_contact_objects: QuerySet[Contact], new_contact_objects: list[Contact]):
    """
    Удаление контактов, которых нет в новом списке новых.
    """
    logger.info('Удаляю старые контакты')

    delete_contacts = exists_contact_objects.exclude(
        abc__in=[obj.abc for obj in new_contact_objects],
        start__in=[obj.start for obj in new_contact_objects],
        end__in=[obj.end for obj in new_contact_objects]
    )
    count = 0
    if delete_contacts.exists():
        count = delete_contacts.count()
        delete_contacts.delete()
    logger.info(f'{count} контактов удалено')


def renew_contacts():
    """
    Главная функция для обновления контактов на основе CSV-файлов из указанных URL-адресов.
    """
    try:
        logger.info('Запуск обновления контактов')
        links = settings.CONTACT_LINKS
        for filename, url in links.items():
            download_file(filename, url)

        logger.info('Создаю объекты новых контактов, для последующего создания, обновления или удаления с сущестующими')
        new_contact_objects = []
        exists_contact_objects = Contact.objects.all()
        for filepath, _ in links.items():
            file: pd.DataFrame = pd.read_csv(filepath, usecols=range(8), sep=';')
            new_contact_objects.extend([
                Contact(
                    abc=row['АВС/ DEF'], 
                    start=row['От'], 
                    end=row['До'], 
                    operator=row['Оператор'], 
                    region=row['Регион'], 
                    territory=row['Территория ГАР'],
                    inn=row['ИНН']
                ) for _, row in file.iterrows()
            ]
            )
        add_or_update_contacts(exists_contact_objects, new_contact_objects)
        delete_from_db_if_not_in_new_list(exists_contact_objects, new_contact_objects)
    except Exception as e:
        logger.error(f'Ошибка обноления контактов -> {e}')
    logger.info('Обновление конктактов завершено')
