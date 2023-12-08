from django.http import HttpResponse
from django.db import models
from django.db.models import Sum, F
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from decimal import Decimal

from .forms import (
    LoginForm,
    UserRegistrationForm,
    UserEditForm,
    ProfileEditForm,
    OrderForm,
)
from .models import Profile, Asset, Order


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request, username=cd["username"], password=cd["password"]
            )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse("Authenticated sucessfully")
                else:
                    return HttpResponse("Disabled account")
            else:
                return HttpResponse("Invalid login")
    else:
        form = LoginForm()
    return render(request, "finance/login.html", {"form": form})


def register(request):
    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet.
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(user_form.cleaned_data["password"])
            # Save the User object
            new_user.save()
            # Create the user profile
            Profile.objects.create(user=new_user)
            return render(request, "finance/register_done.html", {"new_user": new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, "finance/register.html", {"user_form": user_form})


@login_required
def dashboard(request):
    return render(request, "finance/dashboard.html", {"section": "dashboard"})


@login_required
def edit(request):
    if request.method == "POST":
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully")
        else:
            messages.error(request, "Error update your profile")
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(
        request,
        "finance/edit.html",
        {"user_form": user_form, "profile_form": profile_form},
    )


@login_required
def portfolio(request):
    # retrieve portfolio assets
    asset_ids = (
        Order.objects.filter(user=request.user)
        .values_list("asset_id", flat=True)
        .distinct()
    )
    assets = Asset.objects.filter(id__in=asset_ids)

    # initialize portfolio data
    positions = []
    portfolio_value = Decimal("0")
    portfolio_unrealised_gains = Decimal("0")
    portfolio_invested = Decimal("0")
    portfolio_beta = Decimal("0")

    for asset in assets:
        # retrieve buy / sell orders for each asset
        buy_orders = asset.orders.filter(user=request.user, order_type=Order.BUY)
        sell_orders = asset.orders.filter(user=request.user, order_type=Order.SELL)

        buy_data = buy_orders.aggregate(
            total_amount=Sum("amount"), total_value=Sum(F("price") * F("amount"))
        )

        sell_data = sell_orders.aggregate(
            total_amount=Sum("amount"), total_value=Sum(F("price") * F("amount"))
        )

        # calculate remaining amount after buy / sell orders
        amount_bought = buy_data["total_amount"] or 0
        amount_sold = sell_data["total_amount"] or 0
        current_amount = amount_bought - amount_sold

        # calculate the total cost of all buy / sell orders
        value_bought = buy_data["total_value"] or 0
        value_sold = sell_data["total_value"] or 0

        # calculate the current valuation
        last_price = asset.prices.latest("day")
        current_valuation = current_amount * last_price.price

        # calculate unrealised gains
        cost_basis_per_unit = value_bought / amount_bought
        total_cost_basis = (current_amount * cost_basis_per_unit) + value_sold
        unrealised_gains = current_valuation - total_cost_basis

        positions.append(
            {
                "asset": asset,
                "amount": current_amount,
                "price": last_price.price,
                "valuation": current_valuation,
                "unrealised_gains": unrealised_gains,
            }
        )

        # Below code is to check which is the current asset and then apply approiate beta

        portfolio_value += current_valuation
        portfolio_unrealised_gains += unrealised_gains
        portfolio_invested += value_bought - value_sold

        if asset.ticker == "GOOG":
            beta = Decimal("1.34")
        elif asset.ticker == "META":
            beta = Decimal("1.56")
        elif asset.ticker == "AMZN":
            beta = Decimal("1.43")

        # Calculate the contribution of the current asset to portfolio beta
        asset_beta_contribution = beta * (current_valuation / portfolio_value)
        portfolio_beta += asset_beta_contribution
        print(portfolio_beta)

    return render(request, "finance/portfolio.html", locals())


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by("-day")
    return render(request, "finance/list.html", {"orders": orders})


@login_required
def order_create(request):
    form = OrderForm()
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            # set the user and save the new order to the database
            form.instance.user = request.user
            form.save()

    return render(request, "finance/create.html", {"form": form})
