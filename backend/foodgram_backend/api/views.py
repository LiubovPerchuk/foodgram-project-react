from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.db.models.functions import Lower
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Ingredient, Recipe, RecipeIngredients,
                            ShoppingList, Subscription, Tag, Favorite)
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (ActionRecipeSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeInfoSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserSerializer)


User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ("author", "tags")
    ordering_fields = ("name", "created_at", "updated_at")

    def get_serializer_class(self):
        """Метод динамического выбора сериализатора."""
        if self.request.method == "GET":
            return RecipeInfoSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        """Метод создания объекта."""
        serializer.save(author=self.request.user)

    def get_queryset(self):
        """Метод для получения queryset с примененными фильтрами."""
        queryset = super().get_queryset()
        is_favorited = self.request.query_params.get("is_favorited")
        if is_favorited is not None:
            queryset = queryset.filter(favorite_recipe__user=self.request.user)

        is_in_shopping_cart = self.request.query_params.get(
            "is_in_shopping_cart")
        if is_in_shopping_cart is not None:
            queryset = queryset.filter(shopping_list__user=self.request.user)

        if is_favorited is not None and is_in_shopping_cart is not None:
            queryset = queryset.filter(
                favorite_recipe__user=self.request.user,
                shopping_list__user=self.request.user)
        return queryset

    @action(detail=True, methods=("post", "delete"))
    def favorite(self, request, pk=None):
        """Метод для создания/удаления рецепта из списка избранного."""
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.request.method == "POST":
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                raise exceptions.ValidationError("Рецепт уже в избранном.")
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = ActionRecipeSerializer(
                recipe, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        favorite = get_object_or_404(Favorite, user=user, recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=("get",),
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Метод для скачивания списка покупок."""
        shopping_cart = ShoppingList.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        buy_list = RecipeIngredients.objects.filter(
            recipe__in=recipes).values("ingredient").annotate(
            amount=Sum("amount"))
        buy_list_text = "Список покупок с сайта Foodgram:\n\n"
        for item in buy_list:
            ingredient = Ingredient.objects.get(pk=item["ingredient"])
            amount = item["amount"]
            buy_list_text += (
                f"{ingredient.name}, {amount} "
                f"{ingredient.measurement_unit}\n")
        response = HttpResponse(buy_list_text, content_type="text/plain")
        response["Content-Disposition"] = (
            "attachment; filename=shopping-list.txt")
        return response

    @action(detail=True, methods=("post", "delete"))
    def shopping_cart(self, request, pk=None):
        """Метод для создания/удаления рецепта из списка покупок."""
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.request.method == "POST":
            if ShoppingList.objects.filter(user=user, recipe=recipe).exists():
                raise exceptions.ValidationError(
                    "Рецепт уже находится в списке покупок.")
            ShoppingList.objects.create(user=user, recipe=recipe)
            serializer = ActionRecipeSerializer(
                recipe, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        shopping_cart = get_object_or_404(
            ShoppingList, user=user, recipe=recipe)
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ("^name", "name__icontains")
    ordering_fields = ("name",)
    pagination_class = None

    def get_queryset(self):
        """Метод регистронезависимой сортировки по полю name."""
        queryset = super().get_queryset()
        ingredient_query = self.request.query_params.get("name")

        if ingredient_query:
            queryset = queryset.filter(
                name__startswith=ingredient_query[0].lower())
        queryset = queryset.annotate(lower_name=Lower("name"))
        queryset = queryset.order_by("lower_name")
        return queryset


class CustomUserViewSet(UserViewSet):
    """Вьюсет для пользователя."""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(
        detail=False,
        methods=("get",),
        serializer_class=SubscriptionSerializer,
        permission_classes=(IsAuthenticated, ))
    def subscriptions(self, request):
        """Метод получения подписки на пользователя."""
        pages = self.paginate_queryset(
            Subscription.objects.filter(user=request.user))
        serializer = SubscriptionSerializer(
            pages, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=("post", "delete"),
            url_path="subscribe",
            serializer_class=SubscriptionSerializer)
    def subscribe(self, request, **kwargs):
        """Метод создания/удаления подписки на пользователя."""
        user = get_object_or_404(User, id=kwargs.get("id"))
        subscribe = Subscription.objects.filter(
            user=request.user, subscribing=user)
        if request.method == "POST":
            if user == request.user:
                raise exceptions.ValidationError(
                    "Нельзя подписаться на самого себя.")
            try:
                obj, created = Subscription.objects.get_or_create(
                    user=request.user, subscribing=user)
                if not created:
                    raise exceptions.ValidationError("Вы уже подписались.")
                serializer = SubscriptionSerializer(
                    obj, context={"request": request})
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
            except Exception:
                raise exceptions.ValidationError(
                    "Вы уже подписаны.")
        if not subscribe.exists():
            raise exceptions.ValidationError(
                "Подписка не оформлена или уже удалена.")
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
