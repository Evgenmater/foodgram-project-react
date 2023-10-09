from datetime import datetime as dt
from django.db.models import Sum
from django.http import FileResponse
from djoser.views import UserViewSet
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS

from api.filters import FilterForRecipes, FilterForIngredients
from api.permissions import IsAuthorOrReadOnlyPermission
from api.pagination import ModifiedPagination
from api.serializers import (
    TagSerializer, IngredientSerializer, CustomUserSerializer,
    CreateRecipeSerializer, RecipeSerializer, SubscriptionSerializer,
    OptionalRecipeSerializer,
)
from recipes.models import Tag, Ingredient, Recipe, IngredientRecipe

from users.models import User


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Список и информация об ингредиентах."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterForIngredients


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Список и инофрмация о тегах."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class UserViewSet(UserViewSet):
    """
    Получение списка подписок на пользователей с двумя доп. методами:
    1) subscribe - подписка и отписка на других пользователей.
    2) subscriptions - Возвращает пользователей,
    на которых подписан текущий пользователь.
    """

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = ModifiedPagination
    lookup_value_regex = r'\d+'

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        author_recipe = get_object_or_404(User, id=id)
        subscribe_queryset = request.user.subscriber.filter(
            author=id
        )
        if request.method == 'POST':
            if request.user == author_recipe:
                return Response(
                    'Нельзя подписаться на самого себя.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            if subscribe_queryset.exists():
                return Response(
                    'Вы уже подписаны на пользователя.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            request.user.subscriber.create(author=author_recipe)
            serializer = SubscriptionSerializer(
                User.objects.filter(username=author_recipe),
                many=True,
                context={'request': request}
            )
            return Response(
                serializer.data[0],
                status=status.HTTP_201_CREATED
            )
        if subscribe_queryset.exists():
            subscribe_queryset.delete()
            return Response(
                'Вы отписались от автора',
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            'Вы не подписаны на автора',
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        sub_queryset = self.paginate_queryset(
            User.objects.filter(subscribe__user=request.user)
        )
        serializer = SubscriptionSerializer(sub_queryset,
                                            many=True,
                                            context={'request': request})
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    CRUD для рецепта с 4 методами.
    1) get_serializer_class - в взависимости от запроса вызывает сериализатор,
    если для просмотра рецепта RecipesSerializer,
    для остальных запросов CreateRecipeSerializer.
    2) favorite - добавляет или удаляет рецепт из избранного.
    3) shopping_cart - добавляет или удаляет рецепт из покупок.
    4) download_shopping_cart - скачивает ингредиенты в txt формате.
    """

    queryset = Recipe.objects.all()
    pagination_class = ModifiedPagination
    permission_classes = (IsAuthorOrReadOnlyPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterForRecipes
    lookup_value_regex = r'\d+'

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return CreateRecipeSerializer

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        recipe_obj = get_object_or_404(Recipe, id=pk)
        favourite_queryset = request.user.favorited.filter(recipes=recipe_obj)
        if request.method == 'POST':
            if favourite_queryset.exists():
                return Response(
                    'Рецепт добавлен в избранное!',
                    status=status.HTTP_400_BAD_REQUEST
                )
            request.user.favorited.create(recipes=recipe_obj)
            serializer = OptionalRecipeSerializer(recipe_obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if favourite_queryset .exists():
            favourite_queryset.delete()
            return Response(
                'Рецепт удалён из избранного',
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            'Рецепта нету в избранном',
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        recipe_obj = get_object_or_404(Recipe, id=pk)
        shopping_queryset = request.user.shopping.filter(recipes=recipe_obj)
        if request.method == 'POST':
            if shopping_queryset.exists():
                return Response(
                    'Рецепт добавлен в список покупок',
                    status=status.HTTP_400_BAD_REQUEST
                )
            request.user.shopping.create(recipes=recipe_obj)
            serializer = OptionalRecipeSerializer(recipe_obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if shopping_queryset.exists():
            shopping_queryset.delete()
            return Response(
                'Рецепт удалён из списка покупок',
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            'Рецепта нету в списке покупок',
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        shop_ingredient = IngredientRecipe.objects.filter(
            recipes__shopping__user=request.user
        ).values(
            'ingredients__name',
            'ingredients__measurement_unit'
        ).annotate(amount=Sum('amount'))
        file_path = 'shop_list.txt'
        with open(file_path, 'w', encoding='utf8') as f:
            f.write(
                f'Список покупок для {request.user.username}\n'
                f'\nДата покупки - {dt.today():%d.%m.%Y}\n'
            )
            for buy in shop_ingredient:
                f.write(
                    f'\n{buy["ingredients__name"]}'
                    f' {buy["amount"]}'
                    f' {buy["ingredients__measurement_unit"]}'
                    '\n-----------------------------------------------'
                )
            f.write(
                '\n\nСпасибо, что пользуетесь нашим сайтом!'
                ' Будем Ждать вас снова! =)'
            )
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = (
            'attachment; filename="shop_list.txt"'
        )
        return response
