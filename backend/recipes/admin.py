from django.contrib import admin

from . import models


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'favorite')
    list_filter = ('author', 'name', 'tags')

    def favorite(self, obj):
        return obj.favorite.count()


admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.Ingredient, IngredientAdmin)
admin.site.register(models.Recipe, RecipeAdmin)
admin.site.register(models.Cart)
admin.site.register(models.Favorite)
