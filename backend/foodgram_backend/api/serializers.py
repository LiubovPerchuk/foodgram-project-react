from django.core.validators import MinValueValidator
from rest_framework import serializers

from recipes.fields import Base64ImageField
from recipes.models import Ingredient, Recipe, RecipeIngredients, Tag
from recipes.validators import validate_amount
from users.serializers import UserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор на основе модели ингредиента."""

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeIngredientsCreateSerializer(serializers.ModelSerializer):
    """ Сериализатор создания ингредиентов для рецепта."""
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        validators=[validate_amount, MinValueValidator(1)], write_only=True)

    class Meta:
        model = RecipeIngredients
        fields = ("id", "amount")


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientsCreateSerializer(
        many=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())

    class Meta:
        model = Recipe
        fields = ("id", "ingredients", "tags",
                  "image", "name",
                  "text", "cooking_time", "author")
        read_only_fields = ("id", "author",)

    def add_list_ingredients(self, recipe, ingredients):
        """Метод создания списка ингредиентов для рецепта."""
        for ingredient in ingredients:
            RecipeIngredients.objects.create(
                ingredient_id=ingredient.get("id"),
                amount=ingredient.get("amount"),
                recipe=recipe)

    def create(self, validated_data):
        """Метод создания нового рецепта."""
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.add_list_ingredients(recipe, ingredients)
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        """Метод обновления рецепта."""
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        super().update(instance, validated_data)
        instance.ingredients.clear()
        instance.tags.set(tags)
        self.add_list_ingredients(instance, ingredients)
        instance.save()
        return instance

    def validate_name(self, name):
        """Метод валидации поля названия рецепта."""
        if len(name) < 3:
            raise serializers.ValidationError(
                "Название рецепта не может быть короче 3 символов.")
        name = name[0].upper() + name[1:]
        is_exist = Recipe.objects.filter(
            author=self.context["request"].user,
            name=name).exists()
        if is_exist and self.context["request"].method == "POST":
            raise serializers.ValidationError(
                "Рецепт с таким названием уже существует.")
        return name

    def validate_ingredients(self, value):
        """Метод валидации поля ингредиенты."""
        if not value:
            raise serializers.ValidationError(
                "Список ингредиентов не может быть пустым")
        return value

    def validate_text(self, text):
        """Метод валидации поля описания рецепта."""
        if len(text) < 10:
            raise serializers.ValidationError(
                "Описание должно быть длиннее 10 символов.")
        return text[0].upper() + text[1:]

    def validate_cooking_time(self, value):
        """Метод валидации поля времени приготовления рецепта."""
        if value < 1:
            raise serializers.ValidationError(
                "Время приготовления должно быть минимум 1 минуту.")
        return value


class ActionRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор на основе модели рецепта для методов action."""
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор на основе модели тега."""

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class RecipeIngredientsInfoSerializer(serializers.ModelSerializer):
    """Сериализатор для получения ингредиентов для рецепта."""
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit")

    class Meta:
        model = RecipeIngredients
        fields = ("id", "name", "amount", "measurement_unit")


class RecipeInfoSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецепта."""
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientsInfoSerializer(
        many=True, source="recipe_ingredients", read_only=True)
    image = Base64ImageField()
    tags = TagSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField(
        read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True)

    class Meta:
        model = Recipe
        fields = ("id", "tags", "author", "ingredients", "is_favorited",
                  "is_in_shopping_cart", "name", "image", "text",
                  "cooking_time")
        read_only_fields = ("id", "author", "name", "is_favorited",
                            "is_in_shopping_cart")

    def get_is_favorited(self, recipe):
        """Метод проверки рецепта в списке избранного."""
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return recipe.favorites.filter(author=user).exists()

    def get_is_in_shopping_cart(self, recipe):
        """Метод проверки рецепта в списке покупок."""
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return recipe.shopping_cart.filter(author=user).exists()
