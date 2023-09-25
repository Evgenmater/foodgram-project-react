from django.contrib import admin

from recipes.models import (
    Favourite, ShoppingCart, Recipe, Ingredient, Tag, IngredientRecipe
)
from .forms import TagForm

admin.site.empty_value_display = 'Не задано'
admin.site.site_title = 'Админ-панель сайта Фудграм'
admin.site.site_header = 'Админ-панель сайта Фудграм'


class TagAdmin(admin.ModelAdmin):
    form = TagForm
    filter_horizontal = ('questions',)
    fieldsets = (
        (None, {'fields': (('name', 'letter'), 'questions', 'color')}),
    )


class RecipeAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'author',
        'count_favorites'
    )
    list_filter = ('author', 'name', 'tags')
    filter_horizontal = ('ingredients',)

    def count_favorites(self, obj):
        return obj.favorited.count()


class IngredientInRecipeAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientInRecipeAdmin)
admin.site.register(ShoppingCart)
admin.site.register(Favourite)
admin.site.register(Tag)
admin.site.register(IngredientRecipe)
