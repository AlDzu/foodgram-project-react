from rest_framework.generics import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework.relations import SlugRelatedField

from recipes import models
from users.models import Subscriber

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = models.Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = models.Ingredient


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source="ingredient.id",
        required=False
    )
    name = serializers.CharField(
        source="ingredient.name",
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit",
        read_only=True
    )

    class Meta:
        fields = ["id", "name", "measurement_unit", "amount"]
        model = models.RecipeIngredients


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        ]

    def get_is_subscribed(self, obj):
        return False


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(
        many=True,
        source="ingredientsamount"
    )
    tags = TagSerializer(many=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(source="favorite_recipes")
    is_in_shopping_cart = serializers.SerializerMethodField(
        source="shopping_cart"
    )

    class Meta:
        exclude = ['favorite', ]
        model = models.Recipe

    def create(self, validated_data):
        ingredients_amount_data = validated_data.pop("ingredientsamount")
        instance = super().create(validated_data)
        self.ingredients_set(ingredients_amount_data, instance)
        return instance

    def update(self, instance, validated_data):
        ingredients_amount_data = validated_data.pop("ingredientsamount")
        instance = super().update(instance, validated_data)
        models.RecipeIngredients.objects.filter(recipe=instance).delete()
        self.ingredients_set(ingredients_amount_data, instance)

        return instance

    def ingredients_set(self, ingredients_amount_data, recipe_instance):
        ingredients = []
        for ingredient_amount in ingredients_amount_data:
            ingredient_id = ingredient_amount["ingredient"]["id"]
            ingredient = get_object_or_404(models.Ingredient, pk=ingredient_id)
            amount = ingredient_amount["amount"]

            recipe_ingredients_instance = models.RecipeIngredients(
                ingredient=ingredient, recipe=recipe_instance, amount=amount
            )
            ingredients.append(recipe_ingredients_instance)

        models.RecipeIngredients.objects.bulk_create(ingredients)

    def get_favorited(self, recipe):
        user = self.context.get("request").user

        if user.is_anonymous:
            return False

        return recipe.favorite_recipes.filter(user=user).exists()

    def get_in_cart(self, recipe):
        user = self.context.get("request").user

        if user.is_anonymous:
            return False

        return recipe.shopping_cart.filter(user=user).exists()

    def to_internal_value(self, data):
        self.fields["tags"] = serializers.PrimaryKeyRelatedField(
            many=True, queryset=models.Tag.objects.all()
        )
        return super(RecipeSerializer, self).to_internal_value(data)


class CustomRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = [
            "id",
            "name",
            "image",
            "cooking_time",
        ]
        model = models.Recipe


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(
        read_only=True,
        required=False
    )
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        required=False
    )

    class Meta:
        fields = "__all__"
        model = models.Favorite

    def validate(self, attrs):
        request = self.context.get("request")
        recipe_id = self.context.get("view").kwargs.get("recipe_id")
        user = request.user

        is_favorite = user.favorite_recipes.filter(
            recipe_id=recipe_id).exists()

        if is_favorite and request.method == "POST":
            raise ValidationError("Добавлен ранее")
        return attrs

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return CustomRecipeSerializer(instance.recipe, context=context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    user = serializers.PrimaryKeyRelatedField(read_only=True, required=False)

    class Meta:
        fields = "__all__"
        model = models.Cart

    def validate(self, attrs):
        request = self.context.get("request")
        recipe_id = self.context.get("view").kwargs.get("recipe_id")
        user = request.user

        in_cart = user.shopping_cart.filter(recipe_id=recipe_id).exists()

        if in_cart and request.method == "POST":
            raise ValidationError("Рецепт уже в корзине.")
        return attrs

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return CustomRecipeSerializer(instance.recipe, context=context).data


class PreviewRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Recipe
        fields = ("id", "name", "image", "cooking_time")


class UserSubscribeSerializer(serializers.ModelSerializer):
    subscriber = SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    author = SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        fields = "__all__"
        model = Subscriber

    def create(self, validated_data):
        subscriber = validated_data["subscriber"]
        author = validated_data["author"]

        if subscriber == author:
            raise serializers.ValidationError("Подписка на себя")

        if subscriber.authors.filter(author=author).exists():
            raise serializers.ValidationError(
                {"detail": "Уже подписан"}
            )
        return super().create(validated_data)
