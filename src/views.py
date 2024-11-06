import json
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

def load_user_settings(filename: str) -> dict:
    """
    Функция загрузки пользовательских настроек из JSON-файла.
    """
    current_dir = os.path.dirname(__file__)
    full_path = os.path.join(current_dir, '..', filename)
    with open(full_path, 'r') as f:
        return json.load(f)

def fetch_stock_data(symbols: str, start_date: str, end_date: str) -> dict:
    """
    Функция получения исторических данных по акциям за указанный период.
    """
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbols}?from={start_date}&to={end_date}&apikey={API_KEY}"
    response = requests.get(url)

    print(f"Request URL: {url}")
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Content: {response.text}")

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        raise Exception("Unauthorized access. Check your API key.")
    else:
        raise Exception(f"Error fetching data for {symbols}: {response.status_code}")

def fetch_market_data(input_date: str) -> dict:
    """
    Функция получения рыночных данных по пользователю за указанный месяц на основе выбранной даты.

    """
    user_settings = load_user_settings('user_settings.json')
    user_stocks = ','.join(user_settings.get('user_stocks', []))

    date_obj = datetime.strptime(input_date, "%d.%m.%Y")
    start_date = date_obj.replace(day=1).strftime("%Y-%m-%d")
    end_date = date_obj.strftime("%Y-%m-%d")

    market_data = {}

    try:
        stock_data = fetch_stock_data(user_stocks, start_date, end_date)

        for historical_stock in stock_data.get('historicalStockList', []):
            symbol = historical_stock['symbol']
            historical_prices = historical_stock['historical']
            market_data[symbol] = [entry for entry in historical_prices if start_date <= entry['date'] <= end_date]

    except Exception as e:
        print(e)

    return market_data

def get_data_for_date(input_date: str) -> dict:
    """
    Функция получения рыночных данных за конкретный месяц на основе выбранной даты.
    """
    date_obj = datetime.strptime(input_date, "%d.%m.%Y")
    start_date = date_obj.replace(day=1).strftime("%Y-%m-%d")
    end_date = date_obj.strftime("%Y-%m-%d")

    market_data = fetch_market_data(input_date)
    return market_data

# Пример вызова функции
# if __name__ == "__main__":
#     input_date = '22.06.2022'
#     data = get_data_for_date(input_date)
#     print(json.dumps(data, indent=4))