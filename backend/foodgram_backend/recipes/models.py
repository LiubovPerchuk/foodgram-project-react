from django.contrib.auth import get_user_model
from django.db import models

from .validators import hex_color_validator, validate_amount

User = get_user_model()


class Ingredient(models.Model):
    """Модель для описания ингредиентов."""
    name = models.CharField(
        max_length=200,
        verbose_name="Название ингредиента")
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name="Единица измерения ингредиента")

    class Meta:
        ordering = ("name",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


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
        verbose_name="Идентификатор тега")

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
        unique=True,
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
        related_name="tags",
        verbose_name="Тег к рецепту")
    cooking_time = models.PositiveSmallIntegerField(
        default=1,
        validators=[validate_amount],
        blank=True,
        null=True,
        verbose_name="Время приготовления (в минутах)")
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации рецепта")

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
        verbose_name="Рецепт")
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Игредиент")
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=[validate_amount],
        verbose_name="Количество ингредиентов",)

    class Meta:
        verbose_name = "Ингредиент_в_рецепте"
        verbose_name_plural = "Ингредиенты_в_рецепте"

    def __str__(self):
        return (f"{self.ingredient.name} ({self.ingredient.measurement_unit})"
                f" - {self.amount}")


class Favorite(models.Model):
    """Модель для описания списка избранного."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorite_recipe",
        verbose_name="Пользователь")
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorite_recipe",
        verbose_name="Рецепт")

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="unique_favorite_recipe"),)

    def __str__(self):
        return f"Рецепт {self.recipe} добавлен в избранное к {self.user}"


class ShoppingList(models.Model):
    """Модель для описания списка покупок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_list",
        null=True,
        verbose_name="Пользователь")
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_list",
        verbose_name="Рецепт")

    class Meta:
        verbose_name = "Cписок покупок"
        verbose_name_plural = "Списки покупок"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="unique_shopping_list"),)

    def __str__(self):
        return f"Рецепт {self.recipe} добавлен в список покупок к {self.user}"


class Subscription(models.Model):
    """Модель подписки."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user",
        verbose_name="Имя подписчика")
    subscribing = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribing",
        verbose_name="Имя автора")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("user", "subscribing"),
                                    name="unique_subscription")
        ]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"Подписка {self.user} на {self.subscribing}"
