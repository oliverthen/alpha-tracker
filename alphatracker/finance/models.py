from django.db import models


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


class User(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(max_length=50)
    password = models.CharField(max_length=30)
