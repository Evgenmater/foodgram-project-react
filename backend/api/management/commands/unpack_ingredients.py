import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импортирует данные в БД из папки static/data'

    def handle(self, *args, **kwargs):

        with open(
            os.path.join(
                os.path.join(settings.BASE_DIR, 'data'), 'ingredients.csv'
            ),
            'r',
            newline='',
            encoding='utf8'
        ) as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )
