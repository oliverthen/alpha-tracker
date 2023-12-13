# python imports
import requests

# django imports
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# project imports
from finance.models import Asset, Price


class Command(BaseCommand):
    help = "Loads asset tickers and names from Marketstack. Will only do for assets on NYSE or NASDAQ"

    def handle(self, *args, **options):
        # set up the API endpoint URL and parameters
        endpoint = "http://api.marketstack.com/v1/exchanges"

        # make the API request and get the JSON response
        response = requests.get(
            endpoint,
            params={
                "access_key": settings.MARKETSTACK_API_KEY,
            },
        )
        json_response = response.json()
