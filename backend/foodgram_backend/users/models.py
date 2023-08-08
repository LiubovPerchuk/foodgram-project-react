from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""
    USER = "user"
    ADMIN = "admin"

    USER_ROLES = [
        (USER, "Пользователь"),
        (ADMIN, "Администратор")
    ]
    username = models.CharField(
        max_length=150, unique=True,
        verbose_name="Имя пользователя")
    email = models.EmailField(
        max_length=254,
        verbose_name="Электронная почта",
        unique=True)
    first_name = models.CharField(
        max_length=150,
        verbose_name="Имя")
    last_name = models.CharField(
        max_length=150,
        verbose_name="Фамилия")
    password = models.CharField(
        max_length=150,
        verbose_name="Пароль")
    role = models.CharField(
        max_length=20,
        verbose_name="Роль",
        default=USER,
        choices=USER_ROLES)

    class Meta:
        ordering = ("id",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name", "password"]

    def __str__(self):
        return self.email

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_admin(self):
        return self.role == self.ADMIN
