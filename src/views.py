import json
import logging
from datetime import datetime

import pandas as pd

from src.utils import fetch_currency_data, fetch_stock_data, filter_transactions_by_date, load_user_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def get_greeting(current_time):
    """
    Возвращает приветствие в зависимости от текущего времени суток.
    """
    hour = current_time.hour
    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_card_statistics(data):
    """
    Формирует статистику по каждой карте: траты, кешбэк, последние 4 цифры карты.
    """
    card_stats = (
        data.groupby("Номер карты")
        .agg(
            total_spent=("Сумма операции", "sum"),
            cashback=("Сумма операции", lambda x: round(max(x.sum(), 0) * 0.01, 2)),
        )
        .reset_index()
    )
    card_stats["Номер карты"] = card_stats["Номер карты"].str[-4:]
    return card_stats.to_dict(orient="records")


def get_top_transactions(data, top_n=5):
    """
    Возвращает топ-N транзакций по сумме.
    """
    data["Дата операции"] = pd.to_datetime(data["Дата операции"], errors="coerce")
    top_transactions = (
        data[["Дата операции", "Сумма операции", "Категория", "Описание"]]
        .sort_values(by="Сумма операции", ascending=False)
        .head(top_n)
    )
    top_transactions["Дата операции"] = top_transactions["Дата операции"].dt.strftime("%Y-%m-%d")
    return top_transactions.to_dict(orient="records")


def main(date_str, excel_path="../data/operations.xlsx", user_settings_path="../user_settings.json", api_key=None):
    """
    Генерирует JSON-ответ с приветствием, статистикой по картам,
    топовыми транзакциями, курсами валют и ценами акций.
    """
    try:
        data = pd.read_excel(excel_path)
        user_settings = load_user_settings(user_settings_path)

        filtered_data = filter_transactions_by_date(data, date_str)
        currency_data = fetch_currency_data(api_key, user_settings["user_currencies"])
        stock_data = fetch_stock_data(api_key, user_settings["user_stocks"])

        response = {
            "greeting": get_greeting(datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")),
            "cards": get_card_statistics(filtered_data),
            "top_transactions": get_top_transactions(filtered_data),
            "currency_rates": [{"currency": currency, "rate": rate} for currency, rate in currency_data.items()],
            "stock_prices": [{"stock": stock["symbol"], "price": stock["price"]} for stock in stock_data],
        }

        logging.info("JSON-ответ успешно сгенерирован.")
        return json.dumps(response, ensure_ascii=False, indent=4)

    except Exception as e:
        logging.error(f"Ошибка: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False, indent=4)
