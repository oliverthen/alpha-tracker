# python imports
import requests

# django imports
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# project imports
from finance.models import Asset, Price


class Command(BaseCommand):
    help = "Loads asset tickers and names from Marketstack. Will only do for  stocks on NASDAQ at first"

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

        # Need to get total amount of stocks on exchange first to determine how many API requests to make
        total = json_response["pagination"]["total"]
        offset = 0

        counter = 0

        for data in json_response["data"]["tickers"]:
            counter += 1
        print(counter)

        while True and offset < 16000:
            # Offset parameter keeps increasing to get stocks on pages other than the first one
            offset += 1000

            if offset > total:
                # stock list for this exchange has been exhausted
                break

            response = requests.get(
                endpoint,
                params={
                    "access_key": settings.MARKETSTACK_API_KEY,
                    "limit": 1000,
                    "offset": offset,
                },
            )

            json_response = response.json()

            for data in json_response["data"]["tickers"]:
                counter += 1
            print(counter)

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
