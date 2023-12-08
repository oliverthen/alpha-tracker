from django.contrib import admin
from .models import Profile, Asset, Price, Order


@admin.register(Profile)
class ProfileAmin(admin.ModelAdmin):
    list_display = ["user", "date_of_birth"]
    raw_id_fields = ["user"]


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ["ticker", "name"]


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ["asset", "day", "price"]
    date_hierarchy = "day"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["day", "order_type", "amount", "asset", "price", "day"]
    list_filter = ["order_type", "day"]
    date_hierarchy = "day"
