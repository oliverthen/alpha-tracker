import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from finance.models import Asset, Price, Order
from decimal import Decimal

# Below tests need more finetuning

@pytest.fixture
def user_data():
    return {
        "username": "testuser",
        "password": "testpassword",
        "email": "testuser@example.com",
    }


@pytest.fixture
def create_user(db, user_data):
    return User.objects.create_user(**user_data)


@pytest.fixture
def create_asset(db):
    return Asset.objects.create(name="Test Asset", ticker="TEST", category="Stock")


@pytest.fixture
def create_price(db, create_asset):
    return Price.objects.create(asset=create_asset, day="2022-01-01", price=100)


@pytest.fixture
def create_order(db, create_asset, create_user):
    return Order.objects.create(
        asset=create_asset, user=create_user, order_type=Order.BUY, amount=10, price=100
    )


@pytest.fixture
def client(create_user):
    client = Client()
    client.login(username="testuser", password="testpassword")
    return client


def test_portfolio_view(client, create_asset, create_price, create_order):
    # Assuming you have a 'portfolio' URL in your urlpatterns
    url = reverse("finance:portfolio")
    response = client.get(url)

    assert response.status_code == 200
    assert "positions" in response.context
    assert "portfolio_value" in response.context
    assert "portfolio_unrealised_gains" in response.context
    assert "portfolio_invested" in response.context
    assert "portfolio_beta" in response.context

    # Add more assertions based on your specific context data and HTML structure
    # Example:
    assert b"Test Asset" in response.content
    assert Decimal("1000.00") in response.context["portfolio_value"]
    assert Decimal("0.00") in response.context["portfolio_unrealised_gains"]
    assert Decimal("1000.00") in response.context["portfolio_invested"]
    assert Decimal("0.00") in response.context["portfolio_beta"]
