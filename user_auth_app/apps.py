from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_guest_users(sender, **kwargs):
    from .models import CustomUser

    if not CustomUser.objects.filter(username="andrey").exists():
        CustomUser.objects.create_user(
            username="andrey",
            email="guest_customer@test.de",
            password="asdasd",
            type="customer"
        )

    if not CustomUser.objects.filter(username="kevin").exists():
        CustomUser.objects.create_user(
            username="kevin",
            email="guest_business@test.de",
            password="asdasd24",
            type="business"
        )


class UserAuthAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "user_auth_app"

    def ready(self):
        post_migrate.connect(create_guest_users, sender=self)