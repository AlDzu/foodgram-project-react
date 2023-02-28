from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Тег"""

    name = models.CharField("Название", max_length=100)
    color = ColorField("Цвет по HEX", default='#FF0000')
    slug = models.SlugField("Путь", unique=True, max_length=100)

    class Meta:
        verbose_name = "Тег"
        ordering = ("id", )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингредиент"""

    name = models.CharField("Название", max_length=100)
    measurement_unit = models.CharField("Ед. измерения", max_length=100)
    constraints = (
        models.UniqueConstraint(
            fields=("name", "measurement_unit"),
            name="unique_ingredient",
        )
    )

    class Meta:
        verbose_name = "Ингредиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепт"""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="own_recipes"
    )
    name = models.CharField("Название", max_length=100)
    image = models.ImageField(upload_to="recipes/")
    text = models.TextField("Описание", )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredients",
        related_name="recipes"
    )
    tags = models.ManyToManyField(Tag, related_name="recipes")
    cooking_time = models.IntegerField(
        "Время приготовления",
        validators=[MinValueValidator(1)]
        )
    create_date = models.DateTimeField(
        "Дата добавления",
        auto_now_add=True,
        blank=True
    )
    favorite = models.ManyToManyField(
        User,
        through="Favorite",
        related_name="recipes"
    )

    class Meta:
        verbose_name = "Рецепт"
        ordering = ("-create_date", )

    def __str__(self):
        return self.name


class Favorite(models.Model):
    """Избранное"""

    recipe = models.ForeignKey(
        Recipe,
        related_name="favorite_recipes",
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        related_name="favorite_recipes",
        on_delete=models.CASCADE
    )
    constraints = (
        models.UniqueConstraint(
            fields=("recipe", "user"),
            name="unique_favorite",
        )
    )

    class Meta:
        verbose_name = "Избранный рецепт"

    def __str__(self):
        return f"{self.recipe} - {self.user}"


class RecipeIngredients(models.Model):
    """Ингредиенты рецепта"""

    recipe = models.ForeignKey(
        Recipe, related_name="amount", on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name="amount",
        on_delete=models.CASCADE
    )
    amount = models.IntegerField(
        "Количество",
        validators=[MinValueValidator(1)]
    )  # Не менее единицы измерения
    constraints = (
        models.UniqueConstraint(
            fields=("recipe", "ingredient"),
            name="unique_ingredient",
        )
    )

    class Meta:
        verbose_name = "Ингредиент рецепта"

    def __str__(self):
        return (
            f"{self.amount}{self.ingredient.measurement_unit} - "
            + f"{self.ingredient} - {self.recipe}"
        )


class Cart(models.Model):
    """Что купить"""

    recipe = models.ForeignKey(
        Recipe,
        related_name="cart",
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        related_name="cart",
        on_delete=models.CASCADE
    )
    constraints = (
        models.UniqueConstraint(
            name="unique_cart",
            fields=("recipe", "user"),
        )
    )

    class Meta:
        verbose_name = "Список покупок"

    def __str__(self):
        return f"Всё для{self.recipe} в корзине"
