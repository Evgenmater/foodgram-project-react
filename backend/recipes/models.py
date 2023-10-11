from colorfield.fields import ColorField
from django.db import models
from django.core.validators import MinValueValidator, RegexValidator

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        'Название тега',
        max_length=200,
        unique=True,
        db_index=True
    )
    color = ColorField(
        'Цвет тега',
        max_length=7,
        default='#FF0000',
        unique=True,
        validators=[
            RegexValidator(
                regex='^#([A-F0-9]{6}|[A-F0-9]{3})$',
                message=(
                    'Неверное значение! Введите значение в верхнем регистре!'
                )
            )
        ],
    )
    slug = models.SlugField(
        'Идентификатор',
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель для ингредиентов."""

    name = models.CharField(
        'Название ингредиента',
        max_length=200,
        db_index=True
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения ингредиента',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit'
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель для рецептов."""

    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиенты'
    )
    name = models.CharField('Название рецепта', max_length=200, db_index=True)
    image = models.ImageField('Изображение', upload_to='recipes/images/')
    text = models.TextField('Описание',)
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        auto_now_add=True
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        default=1,
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipe'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Связная модель для ингридиента и рецепта."""

    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )

    amount = models.PositiveSmallIntegerField(
        'Количество ингредиентов',
        default=1,
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Ингридиенты и рецепт'
        verbose_name_plural = 'Ингридиенты и рецепты'
        default_related_name = 'ingredient_recipe'
        constraints = [
            models.UniqueConstraint(
                fields=('recipes', 'ingredients'),
                name='unique_ingredient_recipe'
            )
        ]

    def __str__(self):
        return self.ingredients.name


class ShoppingCart(models.Model):
    """Модель для списка покупок."""

    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipes'],
                name='unique_shopping'
            )
        ]

    def __str__(self):
        return self.recipes.name


class Favourite(models.Model):
    """Модель для избранных рецептов."""

    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        default_related_name = 'favorited'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipes'],
                name='unique_favorited'
            )
        ]

    def __str__(self):
        return self.recipes.name
