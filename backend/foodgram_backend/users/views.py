from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import exceptions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from .serializers import SubscriptionSerializer, UserSerializer
from .models import User, Subscription


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
                    user=request.user,
                    subscribing=user
                )
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
