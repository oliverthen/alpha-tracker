from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Sum
from .models import Profile, Order, Asset


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Repeat password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "first_name", "email"]

    def clean_password2(self):
        cd = self.cleaned_data
        if cd["password"] != cd["password2"]:
            raise forms.ValidationError("Passwords don't match.")
        return cd["password2"]

    def clean_email(self):
        data = self.cleaned_data["email"]
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError("Email is already in use.")
        return data


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

    def clean_email(self):
        data = self.cleaned_data["email"]
        qs = User.objects.exclude(id=self.instance.id).filter(email=data)
        if qs.exists():
            raise forms.ValidationError("Email is already in use.")
        return data


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["date_of_birth"]


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = [
            "user",
        ]

    def clean(self):
        cleaned_data = super().clean()
        order_type = cleaned_data.get("order_type")

        if order_type == Order.SELL:
            # don't sell shares that you don't have
            asset = cleaned_data.get("asset")
            amount = cleaned_data.get("amount")
            amount_bought = asset.orders.filter(order_type=Order.BUY).aggregate(
                total_amount=Sum("amount")
            )
            amount_sold = asset.orders.filter(order_type=Order.SELL).aggregate(
                total_amount=Sum("amount")
            )

            amount_bought = amount_bought["total_amount"] or 0
            amount_sold = amount_sold["total_amount"] or 0
            current_amount = amount_bought - amount_sold

            if current_amount - amount < 0:
                raise ValidationError("Cannot sell shares you don't have")


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        exclude = []
