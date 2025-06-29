from django.db import models
from django.core.validators import MinLengthValidator


class Company(models.Model):
    INN_LENGTH = 12

    INN = models.CharField(
        max_length=INN_LENGTH,
        validators=[MinLengthValidator(INN_LENGTH)],
        unique=True
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Storage(models.Model):
    address = models.CharField(max_length=255)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='storages'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.title} = {self.address}"


