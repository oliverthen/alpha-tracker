from django.http import HttpResponse
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
    AssetForm,
)
from .models import Profile, Asset, Order
import numpy as np
import yfinance as yf


def _calculate_current_val(current_amount, last_price):
    return current_amount * last_price.price


def _calculate_unrealised_gains(
    value_bought, amount_bought, current_amount, value_sold, current_valuation
):
    cost_basis_per_unit = value_bought / amount_bought
    total_cost_basis = (current_amount * cost_basis_per_unit) + value_sold
    return current_valuation - total_cost_basis


def _calculate_asset_beta(ticker):
    # Comparing asset's return with NASDAQ Compiste for 2018 to 2022 to evaluate the asset's beta

    asset = yf.Ticker(ticker)

    data = asset.history(start="2018-01-01", end="2023-1-2", interval="3mo")
    open_list = data["Open"].tolist()

    start_year_price = []
    i = 0

    for open_price in open_list:
        # Since interval for history is 3 months, it means there are 4 sets of dates per year. Since we only want the open price for first date of year, we set i to 0, save that price, and then skip over the other prices since i is not 0. Once i becomes 3, we then turn it back to 0 to save that price
        if i == 0:
            start_year_price.append(open_price)
            i += 1
        else:
            if i == 3:
                i = 0
            else:
                i += 1

    asset_returns = []
    prev = None

    for price in start_year_price:
        # Below code calculates yearly return based on comparing prices from year to year
        if prev is None:
            prev = price
        else:
            asset_return = (price - prev) / prev
            asset_returns.append(round(asset_return, 2))
            prev = price

    asset_stock_returns = np.array(asset_returns)
    market_returns = np.array([-0.05, 0.36, 0.39, 0.25, -0.34])

    # Calculate covariance and variance
    asset_covariance = np.cov(asset_stock_returns, market_returns)[0, 1]
    variance_market = np.var(market_returns)

    # Calculate beta for the asset
    asset_beta = asset_covariance / variance_market

    return asset_beta


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
    # portfolio_beta = Decimal("0")

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
        current_valuation = _calculate_current_val(current_amount, last_price)

        # calculate unrealised gains
        unrealised_gains = _calculate_unrealised_gains(
            value_bought, amount_bought, current_amount, value_sold, current_valuation
        )

        positions.append(
            {
                "asset": asset,
                "amount": current_amount,
                "price": last_price.price,
                "valuation": current_valuation,
                "unrealised_gains": unrealised_gains,
            }
        )

        portfolio_value += current_valuation
        portfolio_unrealised_gains += unrealised_gains
        portfolio_invested += value_bought - value_sold

    # Below code calculates portfolio beta
    portfolio_beta = 0
    for position in positions:
        position_weight = position["price"] * position["amount"] / portfolio_value
        asset_beta = _calculate_asset_beta(position["asset"].ticker)
        weighted_beta = float(position_weight) * asset_beta
        portfolio_beta += round(weighted_beta, 2)

    return render(request, "finance/portfolio.html", locals())


@login_required
def order_list(request):
    orders = request.user.orders.all().order_by("-day")
    return render(request, "finance/list.html", {"orders": orders})


@login_required
def order_create(request):
    form = OrderForm()

    if request.method == "GET":
        user_profile = Profile.objects.get(user=request.user)
        form.fields["asset"].queryset = user_profile.assets.all()

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            # set the user and save the new order to the database
            form.instance.user = request.user
            form.save()

    return render(request, "finance/create.html", {"form": form})


@login_required
def add_asset(request):
    if request.method == "POST":
        form = AssetForm(request.POST)
        if form.is_valid():
            # Try to create a new asset
            asset = form.save()

            # Get the user's profile
            user_profile = Profile.objects.get(user=request.user)

            # Associate the asset with the user's profile
            user_profile.assets.add(asset)
        else:
            # Handle the case where form validation fails
            if "ticker" in form.errors:
                # If the asset with the same ticker already exists, retrieve it
                existing_asset = Asset.objects.get(name=form.cleaned_data["name"])

                # Get the user's profile
                user_profile = Profile.objects.get(user=request.user)

                # Associate the existing asset with the user's profile
                user_profile.assets.add
    else:
        form = AssetForm()

    return render(request, "finance/asset.html", {"form": form})
