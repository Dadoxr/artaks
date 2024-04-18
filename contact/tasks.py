from celery import shared_task
from contact.services.proccess_renew_contacts import renew_contacts

@shared_task(queue='tasks')
def task_renew_contact():
    renew_contacts()