from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from recipes.models import Recipe

from .models import Subscription, User


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
        return (not user.is_anonymous
                and Subscription.objects.filter(
                    user=user,
                    subscribing=username
                ).exists())


class SubscribeRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор модели подписки на пользователя."""
    email = serializers.ReadOnlyField(source="subscribing.email")
    id = serializers.ReadOnlyField(source="subscribing.id")
    username = serializers.ReadOnlyField(source="subscribing.username")
    first_name = serializers.ReadOnlyField(source="subscribing.first_name")
    last_name = serializers.ReadOnlyField(source="subscribing.last_name")
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField(
        source="get_recipes_count")

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
        recipes = (
            obj.subscribing.recipe.all()[:int(limit)] if limit
            else obj.subscribing.recipe.all())
        return SubscribeRecipeSerializer(
            recipes,
            many=True).data

    def get_recipes_count(self, obj):
        """Метод получения количества рецептов для подписки."""
        return Recipe.objects.filter(author=obj.subscribing).count()
