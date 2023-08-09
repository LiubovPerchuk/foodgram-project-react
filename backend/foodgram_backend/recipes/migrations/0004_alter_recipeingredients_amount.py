# Generated by Django 4.2.3 on 2023-08-09 07:44

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_remove_shoppinglist_unique_shopping_list_recipe_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredients',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, 'Минимум')], verbose_name='Количество ингредиентов'),
        ),
    ]
