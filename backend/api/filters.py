from django.db.models import Q
from django_filters import filters
from django_filters.rest_framework import FilterSet

from recipes.models import Ingredient, Recipe


class IngredientFilter(FilterSet):
    """Поиск игредиента по названию."""

    name = filters.CharFilter(
        field_name='name', method='get_name_or_contains'
    )

    def get_name_or_contains(self, queryset, name, value):
        return queryset.filter(
            Q(name__istartswith=value) | Q(name__icontains=value)
        ).distinct()

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """Фильтрация рецептов."""

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(recipes_favorited__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(
                recipe_shopping_cart__user=self.request.user
            )
        return queryset
