from django.conf import settings
import requests
import logging
import pandas as pd
from django.db.models.query import QuerySet
from contact.models import Contact

logger = logging.getLogger(__name__)

def _download_file(filename: str, url: str):
    """
    Download file from URL and save it to filename.
    """
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        logger.info(f"File {filename} downloaded successfully.")
    else:
        logger.error(f"Error downloading file {filename}: status code {response.status_code}")


def add_or_update_contacts(exists_contact_objects: QuerySet[Contact], new_contact_objects: list[Contact]):
    """
    Add or update contacts based on the provided lists.
    """
    update_list = []
    add_list = []
    for new_contact in new_contact_objects: 
        exists_contact = exists_contact_objects.filter(abc=new_contact.abc, start=new_contact.start, end=new_contact.end)

        if exists_contact.count() < 2:
            if exists_contact.exists() and new_contact != exists_contact.first():
                exists_contact = exists_contact.first()
                exists_contact.operator = new_contact.operator
                exists_contact.region = new_contact.region
                exists_contact.territory = new_contact.territory
                exists_contact.inn = new_contact.inn
                update_list.append(exists_contact)
            else:
                add_list.append(new_contact)
        else:
            logger.warning(f'Duplicate objects found: {list(exists_contact)}. Function: add_or_update_contacts')

    if update_list:
        Contact.objects.bulk_update(update_list, fields=['operator', 'region', 'territory', 'inn'])
        logger.info(f'{len(update_list)} contacts updated')
    
    if add_list:
        Contact.objects.bulk_create(add_list)
        logger.info(f'{len(add_list)} contacts created')


def delete_from_db_if_not_in_new_list(exists_contact_objects: QuerySet[Contact], new_contact_objects: list[Contact]):
    """
    Delete contacts that are not present in the new list.
    """
    delete_contacts = exists_contact_objects.exclude(
        abc__in=[obj.abc for obj in new_contact_objects],
        start__in=[obj.start for obj in new_contact_objects],
        end__in=[obj.end for obj in new_contact_objects]
    )
    if delete_contacts.exists():
        count = delete_contacts.count()
        delete_contacts.delete()
        logger.info(f'{count} contacts deleted')


def renew_contacts():
    """
    Main function to renew contacts based on CSV files from specified URLs.
    """
    links = settings.CONTACT_LINKS
    for filename, url in links.items():
        _download_file(filename, url)

    exists_contact_objects = Contact.objects.all()
    for filepath, _ in links.items():
        file: pd.DataFrame = pd.read_csv(filepath, usecols=range(8), sep=';')
        new_contact_objects = [
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
    
    add_or_update_contacts(exists_contact_objects, new_contact_objects)
    delete_from_db_if_not_in_new_list(exists_contact_objects, new_contact_objects)
