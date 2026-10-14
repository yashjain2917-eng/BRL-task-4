
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    class Role(models.TextChoices):
        USER = "USER", "User"
        AGENT = "AGENT", "Support Agent"
        ADMIN = "ADMIN", "Admin"

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER
    )

    def __str__(self):
        return self.username
