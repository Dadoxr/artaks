from django.core.management.base import BaseCommand
import asyncio
from contact import tasks

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        tasks.task_renew_contact()