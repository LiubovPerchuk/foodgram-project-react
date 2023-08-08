from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import User


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ("id", "email", "username", "first_name",
                    "last_name", "role")
    search_fields = ("email", "username")
    list_filter = ("email", "username")
    empty_value_display = "-пусто-"
