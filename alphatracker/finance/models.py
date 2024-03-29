from django.db import models
from django.conf import settings
import datetime


class Asset(models.Model):
    ticker = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.ticker} - {self.name}"


class Price(models.Model):
    asset = models.ForeignKey(Asset, related_name="prices", on_delete=models.CASCADE)
    day = models.DateField()
    price = models.DecimalField(max_digits=16, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["asset", "day"], name="asset-day")
        ]

    def __str__(self):
        return f"Price for {self.asset.ticker} on {self.day}"


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    assets = models.ManyToManyField(Asset, related_name="profiles", blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


class Order(models.Model):
    BUY = "BUY"
    SELL = "SELL"
    ORDER_TYPE_CHOICES = (
        (BUY, "Buy"),
        (SELL, "Sell"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="orders",
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True,
    )

    asset = models.ForeignKey(Asset, related_name="orders", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=16, decimal_places=2)
    amount = models.PositiveIntegerField()
    day = models.DateField(default=datetime.date.today)
    order_type = models.CharField(max_length=4, choices=ORDER_TYPE_CHOICES, default=BUY)

    def __str__(self):
        return f"{self.order_type} order for {self.asset.ticker} on {self.day}"

    @property
    def total(self):
        total = self.price * self.amount
        if self.order_type == Order.SELL:
            total *= -1
        return total
