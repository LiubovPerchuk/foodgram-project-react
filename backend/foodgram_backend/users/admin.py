from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import User, Subscription


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ("id", "email", "username", "first_name",
                    "last_name", "role")
    search_fields = ("email", "username")
    list_filter = ("email", "username")
    empty_value_display = "-пусто-"


@admin.register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = ("id", "user", "subscribing")
    search_fields = ("user__email", "subscribing__email")
    empty_value_display = "-пусто-"
