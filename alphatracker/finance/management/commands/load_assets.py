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
        endpoint = "http://api.marketstack.com/v1/exchanges/XNAS/tickers"

        # make the API request and get the JSON response
        response = requests.get(
            endpoint,
            params={
                "access_key": settings.MARKETSTACK_API_KEY,
                "limit": 1000,
            },
        )
        json_response = response.json()

        # print(json_response)

        # json_response["data"]
        counter = 0

        for data in json_response["data"]["tickers"]:
            print(data["symbol"])
            counter += 1
        print(counter)

        # for data in json_response["data"]:
        #     asset = Asset.objects.get(ticker=data["symbol"])

        #     try:
        #         # check if price already exists
        #         price = Price.objects.get(asset=asset)
        #     except Price.DoesNotExist:
        #         price = Price.objects.create(
        #             asset=asset, price=data["adj_close"]
        #         )

        #         print(f"Price for {asset.ticker} on {day} created")
        #     else:
        #         print(f"Price for {asset.ticker} on {day} already exists")
