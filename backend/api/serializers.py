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
    """Сериализатор для пользователя."""

    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed'

        )

    def get_is_subscribed(self, obj):
        """Метод для подписки(True/False)."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.is_subscribed.filter(author=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тега."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Связывающий сериализатор для ингридиентов и рецепта."""

    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount',)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецпта."""

    author = CustomUserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def get_ingredients(self, obj):
        """Метод поля ingredients для вывода ингридиентов."""
        return obj.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredients_recipe__amount')
        )

    def get_is_favorited(self, obj):
        """Метод поля is_favorited с булевым значением."""
        user = self.context.get('request').user
        if user == obj.author:
            return False
        if user.is_anonymous:
            return False
        return user.recipes_favorited.filter(recipes=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Метод поля is_in_shopping_cart с булевым значением."""
        user = self.context.get('request').user
        if user == obj.author:
            return False
        if user.is_anonymous:
            return False
        return user.user_shopping_cart.filter(recipes=obj).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализация данных подписок пользователя."""

    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        """Метод для получения рецептов."""
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        return OptionalRecipeSerializer(
            recipes, many=True, read_only=True
        ).data

    @staticmethod
    def get_recipes_count(obj):
        """Метод для получения количество рецептов."""
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        """Метод для подписки(True/False)"""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.is_subscribed.filter(author=obj).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создание/обновление рецепта."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = IngredientRecipeSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time',
        )

    def validate(self, data):
        """Валидация рецепта для обязательного поля."""
        if 'ingredients' not in data:
            raise ValidationError({'ingredients': 'Это поле обязательное!'})
        if 'tags' not in data:
            raise ValidationError({'tags': 'Это поле обязательное!'})
        return data

    def validate_ingredients(self, value):
        """Валидация для Ингредиента."""
        if not value:
            raise ValidationError(
                'Надо добавить ингредиенты!'
            )
        ingredients_list = []
        for item in value:
            ingredient = get_object_or_404(Ingredient, id=item['id'])
            if ingredient in ingredients_list:
                raise ValidationError(
                    'Вы уже добавили этот ингредиент!'
                )
            if int(item['amount']) <= 0:
                raise ValidationError({
                    'amount': 'Минимальное значение поля - 1!'
                })
            ingredients_list.append(ingredient)
        return value

    def validate_tags(self, value):
        """Валидация для Тега."""
        if not value:
            raise ValidationError('Выберите Тег!')
        tags_list = []
        for tag in value:
            if tag in tags_list:
                raise ValidationError('Вы уже добавили Тег!')
            tags_list.append(tag)
        return value

    def validate_image(self, value):
        """Валидация для image."""
        if not value:
            raise ValidationError('Поле не может быть пустым!')
        return value

    def validate_cooking_time(self, value):
        if not value:
            raise ValidationError(
                'Выберите время приготовления!'
            )
        return value

    def to_representation(self, instance):
        """Метод представления модели."""
        serializer = RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        )
        return serializer.data

    def create(self, validated_data):
        """Метод для создания рецепта."""
        user = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data, author=user)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                ingredients_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
                recipes=recipe)
        return recipe

    def update(self, recipe, validated_data):
        """Метод для обновления рецепта."""
        recipe.ingredients.clear()
        recipe.tags.clear()
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
