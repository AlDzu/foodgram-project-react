from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from . import mixins, serializers
from .filters import CustomSearchFilter, RecipeFilter
from .pagination import OnlyDataPagination
from .permissions import IsAuthorOrStaffOrReadOnly
from recipes import models
from users.models import Subscriber

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthorOrStaffOrReadOnly]
    queryset = models.Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    filterset_fields = ["tags", "author__id"]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=["delete"], detail=True)
    def delete(self, request, *args, **kwargs):
        user = self.request.user
        recipe = get_object_or_404(models.Recipe, pk=kwargs.get("pk"))
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
    pagination_class = OnlyDataPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class IngredientViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = models.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    pagination_class = OnlyDataPagination
    filter_backends = [CustomSearchFilter, ]
    search_fields = ["^name"]


class FavoriteViewSet(mixins.CreateDeleteViewSet):
    serializer_class = serializers.FavoriteSerializer

    def perform_create(self, serializer):
        recipe = get_object_or_404(
            models.Recipe,
            pk=self.kwargs.get("recipe_id")
        )
        title_data = {
            "recipe": recipe,
            "user": self.request.user
        }
        serializer.save(**title_data)

    @action(methods=["delete"], detail=True)
    def delete(self, request, recipe_id):
        user = self.request.user
        recipe = get_object_or_404(models.Recipe, pk=recipe_id)
        favorite = get_object_or_404(
            models.FavoriteRecipe,
            user=user,
            recipe=recipe
        )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ShoppingCartSerializer

    def perform_create(self, serializer):
        recipe = get_object_or_404(
            models.Recipe,
            pk=self.kwargs.get("recipe_id")
        )
        title_data = {"recipe": recipe, "user": self.request.user}
        serializer.save(**title_data)

    def list(self, request, *args, **kwargs):
        user = self.request.user
        queryset = models.Cart.objects.filter(user=user)
        total_ingredients = {}
        for shopping_cart in queryset:
            recipe = shopping_cart.recipe
            recipe_ingredients = serializers.RecipeIngredientsSerializer(
                recipe.ingredientsamount,
                many=True
            ).data

            for ingredient in recipe_ingredients:
                name, amount = ingredient["name"], ingredient["amount"]
                measurement_unit = ingredient["measurement_unit"]
                if total_ingredients.get(name):
                    total_ingredients[name] = {
                        measurement_unit: total_ingredients[name][
                            measurement_unit
                        ]
                        + amount
                    }
                else:
                    total_ingredients[name] = {measurement_unit: amount}

        filename = "basket.txt"
        content = ""
        for ingredient in total_ingredients:
            measurement_unit, amount = total_ingredients[ingredient].popitem()
            content += f"{ingredient} ({measurement_unit}) — {amount}\n"
        response = HttpResponse(content, content_type="text/plain")
        response["Content-Disposition"] = "attachment; filename={0}".format(
            filename
        )
        return response

    @action(methods=["delete"], detail=True)
    def delete(self, request, recipe_id):
        user = self.request.user
        recipe = get_object_or_404(models.Recipe, pk=recipe_id)
        cart = get_object_or_404(models.ShoppingCart, user=user, recipe=recipe)
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserSubscriberViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserSubscribeSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        subscriber = self.request.user.subscribers.all()
        return subscriber

    def perform_create(self, serializer):
        author = get_object_or_404(User, pk=self.kwargs.get("user_id"))
        title_data = {"subscriber": self.request.user, "author": author}
        if serializer.is_valid():
            serializer.save(**title_data)

    @action(methods=["delete"], detail=True)
    def delete(self, request, user_id):
        user = self.request.user
        author = get_object_or_404(User, pk=user_id)
        subscribe = get_object_or_404(
            Subscriber,
            subscriber=user,
            author=author
        )
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def download_shopping_cart(request):
    ingredient_list = "Корзина:"
    ingredients = models.Ingredient.objects.filter(
        recipe__shopping_cart__user=request.user
    ).values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(amount=Sum('amount'))
    for num, i in enumerate(ingredients):
        ingredient_list += (
            f"\n{i['ingredient__name']} - "
            f"{i['amount']} {i['ingredient__measurement_unit']}"
        )
        if num < ingredients.count() - 1:
            ingredient_list += ', '
    file = 'shopping_list'
    response = HttpResponse(ingredient_list, 'Content-Type: application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file}.pdf"'
    return response
