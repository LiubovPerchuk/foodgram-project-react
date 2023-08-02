from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Ingredient, Recipe, RecipeIngredients, Tag


@admin.register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ("id", "name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = "-пусто-"


class IngredientInline(admin.TabularInline):
    model = RecipeIngredients


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ("id", "name", "color", "slug")
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = "-пусто-"


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "author", "pub_date")
    search_fields = ("text", "name")
    list_filter = ("pub_date", "name", "author", "tags")
    inlines = (IngredientInline,)
    empty_value_display = "-пусто-"


@admin.register(RecipeIngredients)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = ("recipe", "ingredient", "amount")
    search_fields = ("ingredient__name",)
    empty_value_display = "-пусто-"
