from django.contrib.auth import get_user_model
from django.db.models import F
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from recipes.fields import Base64ImageField
from recipes.models import (Ingredient, Recipe, RecipeIngredients,
                            Subscription, Tag)

User = get_user_model()

MINTEXT = 10


class UserSigninSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ("id", "first_name", "last_name", "password",
                  "username", "email")


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор на основе модели пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "username",
                  "first_name", "last_name", "is_subscribed")

    def get_is_subscribed(self, username):
        user = self.context["request"].user
        return (not user.is_anonymous and Subscription.objects.filter(
                user=user, subscribing=username).exists())


class SubscribeRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки на рецепты."""
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscriptionSerializer(UserSerializer):
    """Сериализатор для подписки на пользователя."""
    email = serializers.ReadOnlyField(source="subscribing.email")
    id = serializers.ReadOnlyField(source="subscribing.id")
    username = serializers.ReadOnlyField(source="subscribing.username")
    first_name = serializers.ReadOnlyField(source="subscribing.first_name")
    last_name = serializers.ReadOnlyField(source="subscribing.last_name")
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ("email", "id", "username", "first_name", "last_name",
                  "is_subscribed", "recipes", "recipes_count")

    def get_is_subscribed(self, obj):
        """Метод получения подписки на пользователя."""
        return True

    def get_recipes(self, obj):
        """Метод получения рецептов для подписки."""
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        recipes = (obj.subscribing.recipe.all()[:int(limit)]
                   if limit else obj.subscribing.recipe.all())
        return SubscribeRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        """Метод получения количества рецептов для подписки."""
        return obj.subscribing.recipe.count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор на основе модели тега."""

    class Meta:
        model = Tag
        fields = "__all__"
        read_only_fields = ("slug", "color")


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор на основе модели ингредиента."""

    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(
        write_only=True)

    class Meta:
        model = RecipeIngredients
        fields = ("id", "amount")


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""
    author = UserSerializer(
        default=serializers.CurrentUserDefault(), read_only=True)
    ingredients = RecipeIngredientsSerializer(
        many=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Recipe
        fields = ("id", "tags", "author", "ingredients",
                  "name", "image", "text",
                  "cooking_time")

    def validate_name(self, name):
        """Метод валидации для поля названия рецепта."""
        name = name.capitalize()
        is_exist = Recipe.objects.filter(
            author=self.context["request"].user,
            name__iexact=name).exists()
        if is_exist and self.context["request"].method == "POST":
            raise serializers.ValidationError(
                "Рецепт с таким названием уже существует.")
        return name

    def validate_ingredients(self, data):
        """Метод валидации для поля ингредиенты."""
        ingredients = data
        if not ingredients:
            raise serializers.ValidationError(
                "Список ингредиентов не может быть пустым!")

        ingredients_list = []
        for item in ingredients:
            ingredient_id = item["id"]
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(
                    "Передан несуществующий ингредиент!")
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError(
                    "Ингредиенты не могут повторяться!")
            ingredients_list.append(ingredient_id)
        return data

    def validate_text(self, text):
        """Метод валидации для поля описания рецепта."""
        if len(text) < MINTEXT:
            raise serializers.ValidationError(
                "Описание рецепта должно быть длиннее 10 символов.")
        return text.capitalize()

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

    def to_representation(self, instance):
        """Метод преобразования модели в словарь."""
        request = self.context.get("request")
        context = {"request": request}
        return RecipeInfoSerializer(instance, context=context).data


class RecipeInfoSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецепта."""
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    tags = TagSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ("id", "tags", "author", "ingredients", "is_favorited",
                  "is_in_shopping_cart", "name", "image", "text",
                  "cooking_time")
        read_only_fields = ("id", "author", "is_favorited",
                            "is_in_shopping_cart")

    def get_ingredients(self, recipe):
        """Метод получения ингредиентов в рецепте."""
        ingredients = recipe.ingredients.values(
            "id",
            "name",
            "measurement_unit",
            amount=F("recipe_ingredients__amount"))
        return ingredients

    def get_is_favorited(self, recipe):
        """Метод проверки рецепта в списке избранного."""
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return user.favorite_recipe.filter(recipe=recipe.id).exists()

    def get_is_in_shopping_cart(self, recipe):
        """Метод проверки рецепта в списке покупок."""
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return user.shopping_list.filter(recipe=recipe.id).exists()


class ActionRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор на основе модели рецепта для методов action."""
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
