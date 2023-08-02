from django.db.models import Sum
from django.db.models.functions import Lower
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Ingredient, Recipe, RecipeIngredients,
                            ShoppingList, Tag, WishList)
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (ActionRecipeSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeInfoSerializer,
                          TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeInfoSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ("author", "tags")
    ordering_fields = ("name", "created_at", "updated_at")

    def get_serializer_class(self):
        """Метод динамического выбора сериализатора."""
        if self.action == "create" or self.action == "partial_update":
            return RecipeCreateSerializer
        return RecipeInfoSerializer

    def perform_create(self, serializer):
        """Метод создания объекта."""
        serializer.save(author=self.request.user)

    def get_queryset(self):
        """Метод для получения queryset с примененными фильтрами."""
        queryset = super().get_queryset()
        # Фильтрация по избранному
        is_favorite = self.request.query_params.get("is_favorite", None)
        if is_favorite is not None:
            queryset = queryset.filter(favorites__user=self.request.user,
                                       favorites__is_favorite=is_favorite)
        # Фильтрация по списку покупок
        is_in_shopping_list = self.request.query_params.get(
            "is_in_shopping_list", None)
        if is_in_shopping_list is not None:
            queryset = queryset.filter(
                shopping_list__user=self.request.user,
                shopping_list__is_in_shopping_list=is_in_shopping_list)
        return queryset

    @action(detail=True, methods=("post", "delete"))
    def favorite(self, request, pk=None):
        """Метод для создания/удаления рецепта из списка избранного."""
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.request.method == "POST":
            if WishList.objects.filter(user=user, recipe=recipe).exists():
                raise exceptions.ValidationError("Рецепт уже в избранном.")
            WishList.objects.create(user=user, recipe=recipe)
            serializer = ActionRecipeSerializer(
                recipe, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == "DELETE":
            if not WishList.objects.filter(user=user, recipe=recipe).exists():
                raise exceptions.ValidationError(
                    "Рецепта нет в избранном или он уже удален.")
            favorite = get_object_or_404(WishList, user=user, recipe=recipe)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

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

        if self.request.method == "DELETE":
            if not ShoppingList.objects.filter(
                    user=user, recipe=recipe).exists():
                raise exceptions.ValidationError(
                    "Рецепта нет в списке покупок или он уже удален.")
            shopping_cart = get_object_or_404(
                ShoppingList, user=user, recipe=recipe)
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


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
        queryset = super().get_queryset()
        # Дополнительная сортировка по первым, затем по вторым
        queryset = queryset.annotate(lower_name=Lower("name"))
        queryset = queryset.order_by("lower_name")
        return queryset
