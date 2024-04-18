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


def add_or_update_contacts(exists_contacts: list[dict[str, Contact]], new_contacts: list[dict[str, dict[str,str]]]):
    """
    Добавление или обновление контактов на основе списка новых контактов.
    """
    logger.info('Обновляю контакты и добавляю новые')
    
    add_list = []
    updated_contact = 0
    count_steps = 0
    for new_contact in new_contacts:
        count_steps += 1
        if count_steps % 10000 == 0:
            logger.info(f'Обработано {count_steps} записей')
        exists_contact_dict = next((obj for obj in exists_contacts if set(obj.keys()) == set(new_contact.keys())), None)
        new_contact_val = next(iter(new_contact.values()))

        if exists_contact_dict:
            exists_contact_obj: Contact = next(iter(exists_contact_dict.values()))
            updated_fields = False

            for field in ['operator', 'region', 'territory', 'inn']:

                    if new_contact_val[field] != getattr(exists_contact_obj, field):
                        setattr(exists_contact_obj, field, new_contact_val[field])
                        updated_fields = True
                
            if updated_fields:
                exists_contact_obj.save()
                updated_contact += 1
        else:

            nc = Contact(
                abc=int(new_contact_val.get('abc', 123)), 
                start=int(new_contact_val.get('start', 1234)), 
                end=int(new_contact_val.get('end', 1234)), 
                operator=str(new_contact_val.get('operator', 'error')), 
                region=str(new_contact_val.get('region', '1234')), 
                territory=str(new_contact_val.get('territory', '1234')),
                inn=int(new_contact_val.get('inn', 1234))
            )
            if nc.operator != 'error':
                add_list.append(nc)


    if add_list:
        logger.info(f'Начинаю bulk_create {len(add_list)} записей в базу данных')
        Contact.objects.bulk_create(add_list)
    logger.info(f'{len(add_list)} контактов создано и {updated_contact} контактов обновлено')


def delete_from_db_if_not_in_new_list(exists_contacts: list[dict[str, Contact]], new_contacts: list[dict[str, dict[str,str]]]):
    """
    Удаление контактов, которых нет в новом списке новых.
    """
    logger.info('Удаляю старые контакты')

    new_contact_keys = {key for contact in new_contacts for key in contact.keys()}

    delete_contacts: list[Contact] = [next(iter(contact.values())) for contact in exists_contacts if next(iter(contact.keys())) not in new_contact_keys]

    count = 0
    if delete_contacts:
        count = len(delete_contacts)
        for contact in delete_contacts:
            contact.delete()
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
        new_contacts = []
        exists_contacts = [{f'{obj.abc}{obj.start}{obj.end}': obj} for obj in Contact.objects.all()]
        for filepath, _ in links.items():
            file: pd.DataFrame = pd.read_csv(filepath, usecols=range(8), sep=';').dropna()

            new_contacts.extend(
                [
                    {
                        f"{row['АВС/ DEF']}{row['От']}{row['До']}": {
                            'abc':int(row['АВС/ DEF']), 
                            'start':int(row['От']), 
                            'end':int(row['До']), 
                            'operator':str(row['Оператор']), 
                            'region':str(row['Регион']), 
                            'territory':str(row['Территория ГАР']),
                            'inn':int(row['ИНН'])}
                    } for _, row in file.iterrows()
                ]
            )
        add_or_update_contacts(exists_contacts, new_contacts)
        delete_from_db_if_not_in_new_list(exists_contacts, new_contacts)
    except Exception as e:
        logger.error(f'Ошибка обноления контактов -> {e}')
    logger.info('Обновление конктактов завершено')
