from django_filters.rest_framework import filters, FilterSet
from rest_framework.exceptions import AuthenticationFailed

from recipes.models import Ingredient, Recipe, Tag


class FilterForIngredients(FilterSet):
    """
    Фильтрация для ингредиентов по имени(name) от набранных букв, например:
    вводишь буквы "бал" выдаёт все слова из БД - балык, бальзам.
    """

    name = filters.CharFilter(field_name='name', method='filter_ingredient')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def filter_ingredient(self, queryset, name, value):
        return queryset.filter(
            name__istartswith=value
        )


class FilterForRecipes(FilterSet):
    """
    Фильтрация для рецепта по тегу, покупкам и избарнном с 2 методами:
    1) filter_favorited - если в избранном есть рецепт,
    то пользователю сделавший запрос вернёт данный рецепт.
    2) filter_shopping_cart - если в покупках есть рецепт,
    то пользователю сделавший запрос вернёт данный рецепт.
    """

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited', method='filter_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart', method='filter_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_favorited(self, queryset, name, value):
        if self.request.user.is_anonymous:
            raise AuthenticationFailed(
                detail='Нужно авторизоваться!'
            )
        if value:
            return queryset.filter(favorited__user=self.request.user)
        return queryset

    def filter_shopping_cart(self, queryset, name, value):
        if self.request.user.is_anonymous:
            raise AuthenticationFailed(
                detail='Нужно авторизоваться!'
            )
        if value:
            return queryset.filter(shopping__user=self.request.user)
        return queryset
