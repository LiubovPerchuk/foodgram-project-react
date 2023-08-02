import csv
import os

from django.core.management import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Загрузка ингредиентов в базу данных."

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))))
        data_path = os.path.join(
            base_dir, "..", "..", "data", "ingredients.csv")
        with open(data_path, mode="r", encoding="utf-8") as file:
            csv_reader = csv.reader(file, delimiter=",")
            for row in csv_reader:
                _, created = Ingredient.objects.get_or_create(
                    name=row[0],
                    defaults={"measurement_unit": row[1]}
                )
                if created:
                    self.stdout.write(f"Создан ингредиент: {row[0]}")
                else:
                    self.stdout.write(f"Ингредиент {row[0]} уже существует")
            self.stdout.write(self.style.SUCCESS(
                "Ингредиенты успешно загружены."))
