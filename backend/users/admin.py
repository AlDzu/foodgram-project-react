from django.contrib import admin
from django.contrib.auth import get_user_model

from users.models import Subscriber

User = get_user_model()


@admin.register(User)
class UsersAdmin(admin.ModelAdmin):
    list_display = ["username", "email"]
    search_fields = ["username", "email"]


admin.site.register(Subscriber)
