from celery import shared_task
import requests
from django.core.exceptions import ObjectDoesNotExist
from .models import Currency


@shared_task
def update_exchange_rates():
    try:
        response = requests.get('http://api.nbp.pl/api/exchangerates/tables/A/')
        data = response.json()

        currencies = data[0]['rates']

        for currency in currencies:
            code = currency['code']
            name = currency['currency']
            rate = currency['mid']

            try:
                currency_object = Currency.objects.get(code=code)
                currency_object.name = name
                currency_object.exchange_rate = rate
                currency_object.save()
            except Currency.DoesNotExist:
                Currency.objects.create(code=code, name=name, exchange_rate=rate)

        print('Exchange rates updated successfully!')
    except Exception as e:
        print(f'Error updating exchange rates: {e}')

