import json
from datetime import datetime
import requests
import os
from dotenv import load_dotenv
from src.utils import get_greeting
import pandas as pd


# Загрузка переменных окружения
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


def fetch_market_data(input_date: str) -> dict:
    user_settings = load_user_settings('user_settings.json')
    user_stocks = ','.join(user_settings.get('user_stocks', []))

    date_obj = datetime.strptime(input_date, "%d.%m.%Y")
    start_date = date_obj.replace(day=1).strftime("%Y-%m-%d")
    end_date = date_obj.strftime("%Y-%m-%d")

    market_data = {}
    stock_data = fetch_stock_data(user_stocks, start_date, end_date)

    for historical_stock in stock_data.get('historicalStockList', []):
        symbol = historical_stock['symbol']
        historical_prices = historical_stock['historical']
        market_data[symbol] = [entry for entry in historical_prices if start_date <= entry['date'] <= end_date]

    return market_data


def get_data_for_date(input_date: str) -> dict:
    """Функция получения рыночных данных за конкретный месяц на основе выбранной даты."""
    return fetch_market_data(input_date)


def load_operations(file_path):
    # Загрузка данных из файла Excel
    return pd.read_excel(file_path)


def process_operations(operations, input_date):
    # Преобразуем дату из строки в объект datetime
    date_obj = datetime.strptime(input_date, '%Y-%m-%d %H:%M:%S')
    greeting = get_greeting(date_obj)

    # Обрабатываем данные по картам
    cards_data = {}
    top_transactions = []

    for _, row in operations.iterrows():
        last_digits = row['Номер карты'][-4:] if row['Номер карты'] else None
        amount = row['Сумма операции']

        if amount < 0:  # Только расход
            if last_digits not in cards_data:
                cards_data[last_digits] = {'total_spent': 0, 'cashback': 0}
            cards_data[last_digits]['total_spent'] += abs(amount)
            cards_data[last_digits]['cashback'] += abs(amount) / 100

            # Добавляем в список топ транзакций
            top_transactions.append({
                'date': row['Дата операции'].strftime('%Y-%m-%d'),
                'amount': abs(amount),
                'category': row['Категория'],
                'description': row['Описание']
            })

    # Формируем ответ
    cards = [{'last_digits': digits, **data} for digits, data in cards_data.items()]

    response = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions[:5],  # Извлекаем только первые 5 транзакций
        "currency_rates": [],  # Здесь добавим данные по курсам валют
        "stock_prices": []  # Здесь добавим данные по ценам акций
    }

    return json.dumps(response, ensure_ascii=False, indent=4)


def main(input_date):
    operations = load_operations('operations.xlsx')
    response = process_operations(operations, input_date)
    return response