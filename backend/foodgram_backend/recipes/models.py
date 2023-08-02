from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from .validators import hex_color_validator
from users.models import User


class Ingredient(models.Model):
    """Модель для описания ингредиентов."""
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Название ингредиента")
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name="Единица измерения ингредиента")

    class Meta:
        ordering = ("name",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель для описания тега."""
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Название тега")
    color = models.CharField(
        max_length=7,
        unique=True,
        validators=[hex_color_validator],
        verbose_name="Цветовой HEX-код")
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name="Идентификатор тега",
        validators=[RegexValidator(
            r"^[-a-zA-Z0-9_]+$",
            "Введите валидный слаг. Допустимые символы:"
            "латинские буквы, цифры, дефис и подчеркивание.")])

    class Meta:
        ordering = ("name",)
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель для описания рецепта."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipe",
        verbose_name="Автор рецепта")
    name = models.CharField(
        max_length=200,
        verbose_name="Название рецепта")
    image = models.ImageField(
        upload_to="recipes/",
        blank=True,
        null=True,
        verbose_name="Изображение")
    text = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание рецепта")
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredients",
        related_name="ingredients",
        verbose_name="Игредиент для рецепта")
    tags = models.ManyToManyField(
        Tag,
        related_name="recipe",
        verbose_name="Тег к рецепту")
    cooking_time = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name="Время приготовления (в минутах)")
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации рецепта")
    favorites = models.ManyToManyField(
        User,
        related_name="favorites",
        verbose_name="Избранное",
        blank=True)
    shopping_cart = models.ManyToManyField(
        User,
        related_name="shopping_cart",
        verbose_name="Список покупок",
        blank=True)

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    """Модель для описания количества ингредиентов,
    необходимых для рецепта."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Рецепт",)
    ingredient = models.ForeignKey(
        "Ingredient",
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Игредиент")
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(1, "Minimum")],
        verbose_name="Количество ингредиентов")

    class Meta:
        ordering = ("id",)
        verbose_name = "Ингредиент_в_рецепте"
        verbose_name_plural = "Ингредиенты_в_рецепте"

    def __str__(self):
        return f"В рецепте {self.recipe} есть ингредиент {self.ingredient}"


class WishList(models.Model):
    """Модель для описания списка избранного."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="wishlist",
        verbose_name="Пользователь")
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="wishlist",
        verbose_name="Рецепт")

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="unique_wishlist_recipe"),
        )

    def __str__(self):
        return f"Рецепт {self.recipe} добавлен в избранное к {self.user}"


class ShoppingList(models.Model):
    """Модель для описания списка покупок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shoppinglist",
        null=True,
        verbose_name="Пользователь")
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shoppinglist",
        verbose_name="Рецепт")

    class Meta:
        verbose_name = "Cписок покупок"
        verbose_name_plural = "Списки покупок"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="unique_shopping_list_recipe"),)

    def __str__(self):
        return f"Рецепт {self.recipe} добавлен в список покупок к {self.user}"
