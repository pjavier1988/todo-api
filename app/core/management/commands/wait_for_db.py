from django.core.management.base import BaseCommand
from psycopg2 import OperationalError as Psycopg2Error
from django.db.utils import OperationalError
import time


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Waiting database is UP.....")
        is_db_up = False
        while is_db_up is False:
            try:
                self.check(databases=['default'])
                is_db_up = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write(
                    "Database currently unavailable, retry in 1 second...")
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database is Ready!!'))
