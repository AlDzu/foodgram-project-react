from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Сферический пользователь"""

    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=10)
    last_name = models.CharField(max_length=100)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "Пользователь"

    def __str__(self):
        return self.username


class Subscriber(models.Model):
    """Сферический подписчик"""

    subscriber = models.ForeignKey(
        User,
        verbose_name="Подписчик",
        related_name="subscribers",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        related_name="authors",
        on_delete=models.CASCADE,
    )
    constraints = (
        models.UniqueConstraint(
            fields=("subscriber", "author"),
            name="unique_following",
        )
    )

    class Meta:
        verbose_name = "Подписка"
        ordering = ("id", )

    def __str__(self):
        return f"{self.subscriber} подписан на {self.author}"
