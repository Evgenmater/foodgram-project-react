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

#     queryset = Tag.objects.all()
#     serializer_class = TagSerializer
#     permission_classes = (AllowAny,)
#     pagination_class = None


# class RecipeViewSet(viewsets.ModelViewSet):
#     """CRUD для рецепта."""

#     queryset = Recipe.objects.all()
#     serializer_class = RecipeSerializer
#     pagination_class = CustomPagination
#     permission_classes = (IsAuthorOrReadOnly,)
#     filter_backends = (DjangoFilterBackend,)
#     filterset_class = RecipeFilter

#     def get_serializer_class(self):
#         """Метод для вызова определенного сериализатора."""

#         if self.action in ('list', 'retrieve'):
#             return RecipeSerializer
#         elif self.action in ('create', 'partial_update'):
#             return CreateRecipeSerializer

#     @action(
#         methods=['post', 'delete'],
#         detail=True,
#         permission_classes=(IsAuthenticated,),
#     )
#     def shopping_cart(self, request, pk):
#         """Метод для добавления/удаления покупки ингредиентов рецепта."""
#         user = request.user
#         recipe = get_object_or_404(Recipe, id=pk)
#         serializer = OptionalRecipeSerializer(recipe)
#         if request.method == 'POST':
#             if ShoppingCart.objects.filter(user=user, recipes=recipe).exists():
#                 return Response(
#                     f'{recipe.name} есть в списке покупок у пользователя',
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             ShoppingCart.objects.create(user=user, recipes=recipe)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         if request.method == 'DELETE':
#             shopping_obj = ShoppingCart.objects.filter(
#                 user=user,
#                 recipes=recipe
#             )
#             if shopping_obj.exists():
#                 shopping_obj.delete()
#                 return Response(
#                     f'Рецепт {recipe.name} удалён из списка покупок',
#                     status=status.HTTP_204_NO_CONTENT
#                 )
#             return Response(
#                 f'В списке покупок нет рецепта {recipe.name}',
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#     @action(
#         methods=['post', 'delete'],
#         detail=True,
#         permission_classes=(IsAuthenticated,),
#     )
#     def favorite(self, request, pk):
#         """Метод для добавления/удаления рецепта из избранного."""
#         user = request.user
#         recipe = get_object_or_404(Recipe, id=pk)
#         serializer = OptionalRecipeSerializer(recipe)
#         if request.method == 'POST':
#             if Favourite.objects.filter(user=user, recipes=recipe).exists():
#                 return Response(
#                     f'{recipe.name} уже есть в избранном у пользователя',
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             Favourite.objects.create(user=user, recipes=recipe)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         if request.method == 'DELETE':
#             favourite_obj = Favourite.objects.filter(user=user, recipes=recipe)
#             if favourite_obj .exists():
#                 favourite_obj .delete()
#                 return Response(
#                     f'Рецепт {recipe.name} удалён из избранного',
#                     status=status.HTTP_204_NO_CONTENT
#                 )
#             return Response(
#                 f'В избранном нет рецепта {recipe.name}',
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#     @staticmethod
#     def txt_file_ingredients(ingredients):
#         """Метод для добавление ингредиентов в список для загрузки."""
#         list_shopping = ''
#         for ingredient in ingredients:
#             list_shopping += (
#                 f'{ingredient["ingredient__name"]}  - '
#                 f'{ingredient["sum"]}'
#                 f'({ingredient["ingredient__measurement_unit"]})\n'
#             )
#         return list_shopping

#     @action(
#         detail=False,
#         methods=('get',),
#         permission_classes=(IsAuthenticated,),
#         url_path='download_shopping_cart',
#         url_name='download_shopping_cart',
#     )
#     def download_shopping_cart(self, request):
#         """
#         Метод для загрузки ингредиентов из выбранных рецептов.
#         """
#         ingredients = IngredientRecipe.objects.filter(
#             recipe__shopping_recipe__user=request.user
#         ).values(
#             'ingredient__name',
#             'ingredient__measurement_unit'
#         ).annotate(sum=Sum('amount'))
#         list_shopping = self.txt_file_ingredients(ingredients)
#         return HttpResponse(list_shopping, content_type='text/plain')


# class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
#     """Список ингредиентов и инофрмация о конкретном ингредиенте."""

#     queryset = Ingredient.objects.all()
#     serializer_class = IngredientSerializer
#     permission_classes = (AllowAny,)
#     pagination_class = None
#     filter_backends = (DjangoFilterBackend,)
#     filterset_class = IngredientFilter
#     search_fields = ('^name',)


# class UserViewSet(UserViewSet):
#     """CRUD для пользователя."""

#     queryset = User.objects.all()
#     serializer_class = CustomUserSerializer
#     permission_classes = (IsAuthenticatedOrReadOnly,)
#     pagination_class = CustomPagination

#     @action(
#         methods=['post', 'delete'],
#         detail=True,
#         permission_classes=(IsAuthenticated,),
#     )
#     def subscribe(self, request, id):
#         """Метод для подписки/отписки на/от пользователя."""
#         user = request.user
#         author = get_object_or_404(User, id=id)
#         change_of_status = Subscription.objects.filter(
#             user=user.id, author=author.id
#         )
#         queryset = User.objects.filter(username=author)
#         serializer = SubscriptionSerializer(
#             queryset,
#             many=True,
#             context={'request': request}
#         )
#         if request.method == 'POST':
#             if user == author:
#                 return Response(
#                     'Нельзя подписаться на самого себя.',
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             if change_of_status.exists():
#                 return Response(
#                     'Вы уже подписаны на пользователя.',
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             subscriber = Subscription.objects.create(
#                 user=user,
#                 author=author
#             )
#             subscriber.save()
#             return Response(
#                 serializer.data[0],
#                 status=status.HTTP_201_CREATED
#             )
#         if change_of_status.exists():
#             change_of_status.delete()
#             return Response(
#                 f'Вы отписались от {author}',
#                 status=status.HTTP_204_NO_CONTENT
#             )
#         return Response(
#             f'Вы не подписаны на пользователя {author}',
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     @action(
#         methods=['get'],
#         detail=False,
#         permission_classes=(IsAuthenticated,),
#     )
#     def subscriptions(self, request):
#         """Метод для просмотра подписок, на которых подписан пользователь."""
#         queryset = self.paginate_queryset(
#             User.objects.filter(subscribe__user=request.user)
#         )
#         serializer = SubscriptionSerializer(queryset,
#                                             many=True,
#                                             context={'request': request})
#         return self.get_paginated_response(serializer.data)
