from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """Custom user model extending AbstractUser with unique email and account type."""

    CUSTOMER = "customer"
    BUSINESS = "business"

    TYPE_CHOICES = [
        (CUSTOMER, "Customer"),
        (BUSINESS, "Business"),
    ]

    email = models.EmailField(unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=CUSTOMER)

    def __str__(self):
        """Return a string representation showing the username and account type."""
        return f"{self.username} ({self.type})"
