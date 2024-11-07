import json
from datetime import datetime
import requests
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
API_KEY = os.getenv("API_KEY")


def load_user_settings(filename: str) -> dict:
    """Функция загрузки пользовательских настроек из JSON-файла."""
    current_dir = os.path.dirname(__file__)
    full_path = os.path.join(current_dir, '..', filename)
    with open(full_path, 'r') as f:
        return json.load(f)


def fetch_stock_data(symbols: str, start_date: str, end_date: str) -> dict:
    """Функция получения исторических данных по акциям за указанный период."""
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbols}?from={start_date}&to={end_date}&apikey={API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        raise Exception("Unauthorized access. Check your API key.")
    else:
        raise Exception(f"Error fetching data for {symbols}: {response.status_code}")


def fetch_currency_data(currencies: list) -> dict:
    """Функция получения текущих курсов валют."""
    url = f"https://financialmodelingprep.com/api/v3/quote/{','.join(currencies)}?apikey={API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        raise Exception("Unauthorized access. Check your API key.")
    else:
        raise Exception(f"Error fetching currency data: {response.status_code}")


def fetch_market_data(input_date: str) -> dict:
    try:
        user_settings = load_user_settings('user_settings.json')
        user_stocks = ','.join(user_settings.get('user_stocks', []))
        user_currencies = user_settings.get('user_currencies', [])

        date_obj = datetime.strptime(input_date, "%d.%m.%Y")
        start_date = date_obj.replace(day=1).strftime("%Y-%m-%d")
        end_date = date_obj.strftime("%Y-%m-%d")

        market_data = {}

        stock_data = fetch_stock_data(user_stocks, start_date, end_date)
        for historical_stock in stock_data.get('historicalStockList', []):
            symbol = historical_stock['symbol']
            historical_prices = historical_stock['historical']
            market_data[symbol] = [entry for entry in historical_prices if start_date <= entry['date'] <= end_date]

        currency_data = fetch_currency_data(user_currencies)
        market_data['currency_rates'] = {currency['symbol']: currency['price'] for currency in currency_data}

        return market_data
    except Exception as e:
        print(str(e))
        return {}


def get_data_for_date(input_date: str) -> dict:
    """Функция получения рыночных данных за конкретный месяц на основе выбранной даты."""
    return fetch_market_data(input_date)

# if __name__ == "__main__":
#     # Пример вызова функции загрузки пользовательских настроек
#     try:
#         settings = load_user_settings("user_settings.json")
#         print("User settings loaded:", settings)
#     except Exception as e:
#         print("Error loading user settings:", str(e))
#
#     # Пример вызова функции получения рыночных данных
#     input_date = "22.06.2022"
#     market_data = fetch_market_data(input_date)
#     print(f"Market data for {input_date}:", market_data)
#
#     # Пример вызова функции получения данных об акциях
#     try:
#         stock_data = fetch_stock_data("AAPL", "2022-06-01", "2022-06-30")
#         print("Stock data for AAPL:", stock_data)
#     except Exception as e:
#         print("Error fetching stock data:", str(e))
#
#     # Пример вызова функции получения данных о валюте
#     try:
#         currency_data = fetch_currency_data(["USD", "EUR"])
#         print("Currency data:", currency_data)
#     except Exception as e:
#         print("Error fetching currency data:", str(e))
#
#     # Пример вызова функции получения данных за определенную дату
#     try:
#         data_for_date = get_data_for_date(input_date)
#         print(f"Data for {input_date}:", data_for_date)
#     except Exception as e:
#         print("Error getting data for date:", str(e))