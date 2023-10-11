from django.db.models import F
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField

from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag
from users.models import User


class OptionalRecipeSerializer(serializers.ModelSerializer):
    """Дополнительный сериализатор для рецептов."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class CustomUserSerializer(UserSerializer):
    """
    Сериализатор для вывода пользователей с 1 методомом:
    get_is_subscribed - для определения подписки на пользователя,
    если пользователь подписан на автора - True, если нет - False.
    """

    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.subscriber.filter(author=obj).exists()
        return False


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода рецептов и их параметров c 3 методами:
    1) get_ingredients - для вывода описания продукта поля ingredients.
    2) get_is_in_shopping_cart - для определении рецепта в покупках,
    если пользователь добавил рецепт в список покупок - True, если нет - False.
    3) get_is_favorited - для определении рецепта в избранном,
    если пользователь добавил рецепт в избранное - True, если нет - False.
    """

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    is_favorited = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def get_ingredients(self, obj):
        return obj.ingredients.values().annotate(
            amount=F('ingredient_recipe__amount')
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.shopping.filter(recipes=obj).exists()
        return False

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.favorited.filter(recipes=obj).exists()
        return False


class IngredientForRecipeSerializer(serializers.ModelSerializer):
    """Связывающий сериализатор для создания ингридиентов в рецепте."""

    id = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount',)


class CreateRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создание или обновление рецепта с 2 методами:
    1) create - Для создания рецепта.
    2) update - Для обновления рецепта
    """

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = IngredientForRecipeSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time',
        )

    def validate(self, data):
        if 'ingredients' not in data:
            raise ValidationError({'ingredients': 'Обязательное поле!'})
        elif 'tags' not in data:
            raise ValidationError({'tags': 'Обязательное поле!'})
        elif 'cooking_time' not in data:
            raise ValidationError({'cooking_time': 'Обязательное поле!'})
        return data

    def validate_tags(self, value):
        if not value:
            raise ValidationError('Нужно выбрать Тег!')
        tags_list = []
        for tag in value:
            if tag in tags_list:
                raise ValidationError('Тег уже добавлен!')
            tags_list.append(tag)
        return value

    def validate_ingredients(self, ingredients):
        ingredient_id = Ingredient.objects.values_list('id', flat=True)
        for ing in ingredients:
            if ing['id'] not in ingredient_id:
                raise ValidationError(
                    'Такого ингредиента не существует!'
                )
        if not ingredients:
            raise ValidationError(
                'Нужно добавить ингредиенты!'
            )
        ingredients_list = []
        for product in ingredients:
            ingredient = get_object_or_404(Ingredient, id=product['id'])
            if ingredient in ingredients_list:
                raise ValidationError(
                    'Этот ингредиент добавлен!'
                )
            elif 'amount' not in product:
                raise ValidationError({
                    'amount': 'обязательное поле!'
                })
            ingredients_list.append(ingredient)
        return ingredients

    def validate_image(self, image):
        if not image:
            raise ValidationError({'image': 'Обязательное поле!'})
        return image

    def validate_cooking_time(self, cooking_time):
        if not cooking_time:
            raise ValidationError(
                'Нужно написать время приготовления!'
            )
        return cooking_time

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        )
        return serializer.data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context.get('request').user,
        )
        recipe.tags.set(tags)
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                ingredients_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
                recipes=recipe)
        return recipe

    def update(self, recipe, validated_data):
        recipe.tags.clear()
        recipe.ingredients.clear()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe.tags.set(tags)
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                ingredients_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
                recipes=recipe
            )
        return super().update(recipe, validated_data)


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализация для подписок пользователя с дополнительными полями,
    recipes, recipes_count, is_subscribed и 3 методами для этих полей.
    1) get_is_subscribed - для определения подписки на пользователя,
    если пользователь подписан на автора - True, если нет - False.
    2) get_recipes_count - для вывода количество рецептов у автора,
    на которого подписан пользователь.
    3) get_recipes - для получения и изменения количества выводимых рецептов
    у автора на которого подписан пользователь.
    """

    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.subscriber.filter(author=obj).exists()
        return False

    def get_recipes_count(self, obj):
        return obj.recipe.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        count_limit = request.GET.get('recipes_limit')
        recipe_obj = obj.recipe.all()
        if count_limit:
            recipe_obj = recipe_obj[:int(count_limit)]
        return OptionalRecipeSerializer(
            recipe_obj, many=True
        ).data
