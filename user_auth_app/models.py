from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    CUSTOMER = "customer"
    BUSINESS = "business"

    TYPE_CHOICES = [
        (CUSTOMER, "Customer"),
        (BUSINESS, "Business"),
    ]

    email = models.EmailField(unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=CUSTOMER)

    def __str__(self):
        return f"{self.username} ({self.type})"
