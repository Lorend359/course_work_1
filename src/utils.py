import json
import logging

import pandas as pd
import requests


def load_user_settings(file_path):
    """
    Загружает настройки пользователя из файла.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def filter_transactions_by_date(data, input_date):
    """
    Фильтрует транзакции по указанному диапазону дат.
    """
    data["Кэшбэк"] = data["Кэшбэк"].fillna(0)
    data = data.dropna(subset=["Номер карты"])
    data.loc[:, "Дата операции"] = pd.to_datetime(data["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")
    data = data.dropna(subset=["Дата операции"])

    input_date = pd.to_datetime(input_date)
    start_date = input_date.replace(day=1)
    end_date = input_date

    filtered_data = data[(data["Дата операции"] >= start_date) & (data["Дата операции"] <= end_date)]
    logging.info(f"Filtered transactions count: {filtered_data.shape[0]}")
    return filtered_data


def fetch_currency_data(api_key, currencies):
    """
    Получает курсы валют через API.
    """
    base_url = "https://financialmodelingprep.com/api/v3/forex"
    response = requests.get(f"{base_url}?apikey={api_key}")

    if response.status_code == 200:
        data = response.json().get("forexList", [])
        currency_data = {
            currency: float(entry["bid"])
            for entry in data
            for currency in currencies
            if entry["ticker"].endswith(f"/{currency}")
        }
        logging.info(f"Filtered currency data: {currency_data}")
        return currency_data
    else:
        raise Exception("Ошибка при получении данных о курсах валют")


def fetch_stock_data(api_key, stocks):
    """
    Получает текущие цены на акции через API.
    """
    symbols = ",".join(stocks)
    base_url = f"https://financialmodelingprep.com/api/v3/quote/{symbols}?apikey={api_key}"
    response = requests.get(base_url)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Ошибка при получении данных о ценах на акции")