from django.contrib import admin
from .models import Offer, OfferDetail

# Register your models here.
@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "user", "created_at", "updated_at"]

@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    list_display = ["id", "offer", "offer_type", "price", "delivery_time_in_days"]