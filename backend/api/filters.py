from django_filters import rest_framework
from rest_framework import filters

from recipes import models


class RecipeFilter(rest_framework.FilterSet):
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        queryset=models.Tag.objects.all(),
        to_field_name="slug",
    )
    is_favorited = rest_framework.CharFilter(method="filter_favorited")
    is_in_shopping_cart = rest_framework.CharFilter(
        method="filter_shopping_cart"
    )

    class Meta:
        model = models.Recipe
        fields = ["tags", "author"]

    def filter_favorited(self, queryset, name, value):
        if value == "True":
            return queryset.filter(favorite_recipes__user=self.request.user)
        return queryset

    def filter_shopping_cart(self, queryset, name, value):
        if value == "True":
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class CustomSearchFilter(filters.SearchFilter):
    search_param = "name"
