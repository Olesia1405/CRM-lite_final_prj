from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )
    is_company_owner = models.BooleanField(default=False)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=255, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

