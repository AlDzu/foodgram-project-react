from django.contrib import admin

from . import models


class TagAdmin(admin.ModelAdmin):
    list_display = ('name')


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit", )
    list_filter = ("measurement_unit", )
    search_fields = ("name", )


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "get_favorite", )
    list_filter = ("author", "tags", )
    search_fields = ("name", "author__username", "tags__name", )

    def favorite(self, obj):
        return obj.favorite.count()


admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.Ingredient, IngredientAdmin)
admin.site.register(models.Recipe, RecipeAdmin)
admin.site.register(models.Cart)
admin.site.register(models.Favorite)
