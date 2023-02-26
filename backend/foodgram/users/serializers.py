from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework.fields import SerializerMethodField

User = get_user_model()


class UserSerializer(BaseUserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        ]
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return user.subscribers.filter(author=obj).exists()
