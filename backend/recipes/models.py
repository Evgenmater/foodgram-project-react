from colorfield.fields import ColorField
from django.core.validators import RegexValidator
from django.db import models

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
        unique=True,
        default='#FF0000',
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message=(
                    'Неверное значение! Введите значение в формате HEX!'
                )
            )
        ],
        help_text=(
            'Введите цвет тега в формате: "0-9, a-f, A-F",например: #B04A7D'
        ),
    )
    slug = models.SlugField(
        'Идентификатор',
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'color', 'slug'),
                name='unique_tags',
            ),
        )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель для ингридиентов."""

    name = models.CharField('Название', max_length=200, db_index=True)
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель для рецептов."""

    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
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
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Связная модель для ингридиента и рецепта."""

    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='Рецепт',
    )
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredients_recipe',
    )

    amount = models.PositiveSmallIntegerField(
        'Количество',
    )

    class Meta:
        verbose_name = 'Ингридиент и рецепт'
        verbose_name_plural = 'Ингридиент и рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=('recipes', 'ingredients'),
                name='unique_ingredients_in_recipe'
            )
        ]

    def __str__(self):
        return self.ingredients.name


class ShoppingCart(models.Model):
    """Модель для списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_cart'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipes'],
                name='unique_shoppingcart'
            )
        ]

    def __str__(self):
        return self.recipes.name


class Favourite(models.Model):
    """Модель для избранных рецептов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        default_related_name = 'favorited'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipes'],
                name='unique_favourite'
            )
        ]

    def __str__(self):
        return self.recipes.name
