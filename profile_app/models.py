from django.db import models
from django.conf import settings


class Profile(models.Model):
    """Profile model storing additional user information linked to a CustomUser."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="profile"
    )
    first_name = models.CharField(max_length=100, blank=True, default="")
    last_name = models.CharField(max_length=100, blank=True, default="")
    file = models.FileField(upload_to="profiles/", blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, default="")
    tel = models.CharField(max_length=50, blank=True, default="")
    description = models.TextField(blank=True, default="")
    working_hours = models.CharField(max_length=100, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a string representation displaying the profile owner's username."""
        return f"Profile of {self.user.username}"

