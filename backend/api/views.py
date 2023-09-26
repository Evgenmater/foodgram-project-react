from datetime import datetime

from django.db.models import Sum
from django.http import HttpResponse
from djoser.views import UserViewSet
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (
    AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
)

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.pagintaion import CustomPagination
from api.serializers import (
    TagSerializer, IngredientSerializer, RecipeSerializer,
    CreateRecipeSerializer, CustomUserSerializer,
    SubscriptionSerializer, OptionalRecipeSerializer,
)
from recipes.models import (
    Tag, Ingredient, Recipe, Favourite, ShoppingCart, IngredientRecipe
)

from users.models import Subscription, User


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Список тегов и инофрмация о конкретном теге."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """CRUD для рецепта."""

    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Метод для вызова определенного сериализатора."""
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer

        elif self.action in ('create', 'partial_update'):
            return CreateRecipeSerializer

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        """Метод для добавления/удаления покупки ингредиентов рецепта."""
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':

            if ShoppingCart.objects.filter(user=user, recipes=recipe).exists():
                return Response(
                    f'{recipe.name} есть в списке покупок у пользователя',
                    status=status.HTTP_400_BAD_REQUEST
                )

            ShoppingCart.objects.create(user=user, recipes=recipe)
            serializer = OptionalRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            shopping_obj = ShoppingCart.objects.filter(
                user=user,
                recipes=recipe
            )

            if shopping_obj.exists():
                shopping_obj.delete()
                return Response(
                    f'Рецепт {recipe.name} удалён из списка покупок',
                    status=status.HTTP_204_NO_CONTENT
                )

            return Response(
                f'В списке покупок нет рецепта {recipe.name}',
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        """Метод для добавления/удаления рецепта из избранного."""
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':

            if Favourite.objects.filter(user=user, recipes=recipe).exists():
                return Response(
                    f'{recipe.name} уже есть в избранном у пользователя',
                    status=status.HTTP_400_BAD_REQUEST
                )

            Favourite.objects.create(user=user, recipes=recipe)
            serializer = OptionalRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            favourite_obj = Favourite.objects.filter(user=user, recipes=recipe)

            if favourite_obj .exists():
                favourite_obj .delete()
                return Response(
                    f'Рецепт {recipe.name} удалён из избранного',
                    status=status.HTTP_204_NO_CONTENT
                )

            return Response(
                f'В избранном нет рецепта {recipe.name}',
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Метод для скачивания ингредиентов в txt формате."""
        user = request.user

        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ingredients = IngredientRecipe.objects.filter(
            recipes__shopping_cart__user=request.user
        ).values(
            'ingredients__name',
            'ingredients__measurement_unit'
        ).annotate(amount=Sum('amount'))

        today = datetime.today()
        shopping_list = (
            f'Список покупок для: {user.get_full_name()}\n\n'
            f'Дата: {today:%Y-%m-%d}\n\n'
        )

        shopping_list += '\n'.join([
            f'- {ingredient["ingredients__name"]} '
            f'({ingredient["ingredients__measurement_unit"]})'
            f' - {ingredient["amount"]}'
            for ingredient in ingredients
        ])

        shopping_list += '\n\nСпасибо, что пользуетесь сайтом Foodgram!'
        file_name = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Список ингредиентов и инофрмация о конкретном ингредиенте."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)


class UserViewSet(UserViewSet):
    """CRUD для пользователя."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        """Метод для подписки/отписки на/от пользователя."""
        user = request.user
        author = get_object_or_404(User, id=id)
        change_of_status = Subscription.objects.filter(
            user=user.id, author=author.id
        )
        queryset = User.objects.filter(username=author)
        serializer = SubscriptionSerializer(
            queryset,
            many=True,
            context={'request': request}
        )

        if request.method == 'POST':

            if user == author:
                return Response(
                    'Нельзя подписаться на самого себя.',
                    status=status.HTTP_400_BAD_REQUEST
                )

            if change_of_status.exists():
                return Response(
                    'Вы уже подписаны на пользователя.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscriber = Subscription.objects.create(
                user=user,
                author=author
            )
            subscriber.save()
            return Response(
                serializer.data[0],
                status=status.HTTP_201_CREATED
            )

        if change_of_status.exists():
            change_of_status.delete()
            return Response(
                f'Вы отписались от {author}',
                status=status.HTTP_204_NO_CONTENT
            )

        return Response(
            f'Вы не подписаны на пользователя {author}',
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        """Метод для просмотра подписок, на которых подписан пользователь."""
        queryset = self.paginate_queryset(
            User.objects.filter(subscribe__user=request.user)
        )
        serializer = SubscriptionSerializer(queryset,
                                            many=True,
                                            context={'request': request})
        return self.get_paginated_response(serializer.data)
