import json
from datetime import datetime

import pandas as pd
import pytest

from src.views import get_card_statistics, get_greeting, get_top_transactions, main


@pytest.fixture
def sample_transactions():
    """
    Пример данных о транзакциях.
    """
    data = pd.DataFrame(
        {
            "Дата операции": ["01.12.2021 12:00:00", "15.12.2021 11:59:59", "31.12.2021 12:00:00"],
            "Сумма операции": [1000, 500, -200],
            "Кэшбэк": [10, 5, 0],
            "Номер карты": ["*1234", "*5678", "*9012"],
            "Категория": ["Пополнение", "Оплата", "Снятие"],
            "Описание": ["Описание1", "Описание2", "Описание3"],
        }
    )
    return data


def test_get_greeting():
    """
    Тестирует функцию генерации приветствия.
    """
    assert get_greeting(datetime(2021, 12, 31, 9, 0)) == "Доброе утро"
    assert get_greeting(datetime(2021, 12, 31, 15, 0)) == "Добрый день"
    assert get_greeting(datetime(2021, 12, 31, 20, 0)) == "Добрый вечер"
    assert get_greeting(datetime(2021, 12, 31, 2, 0)) == "Доброй ночи"


def test_get_card_statistics(sample_transactions):
    """
    Тестирует подсчет статистики по картам.
    """
    stats = get_card_statistics(sample_transactions)
    assert len(stats) == 3
    assert stats[0]["total_spent"] == 1000
    assert stats[0]["cashback"] == 10
    assert stats[1]["total_spent"] == 500
    assert stats[1]["cashback"] == 5


def test_get_top_transactions(sample_transactions):
    """
    Тестирует выбор топ-N транзакций.
    """
    top_transactions = get_top_transactions(sample_transactions, top_n=2)
    assert len(top_transactions) == 2
    assert top_transactions[0]["Сумма операции"] == 1000
    assert top_transactions[1]["Сумма операции"] == 500


def test_main(monkeypatch, tmp_path, sample_transactions):
    """
    Тестирует функцию main.
    """

    def mock_fetch_currency_data(api_key, currencies):
        return {"USD": 1.00, "EUR": 0.85}

    def mock_fetch_stock_data(api_key, stocks):
        return [{"symbol": "AAPL", "price": 150.00}, {"symbol": "GOOGL", "price": 2800.00}]

    monkeypatch.setattr("src.views.fetch_currency_data", mock_fetch_currency_data)
    monkeypatch.setattr("src.views.fetch_stock_data", mock_fetch_stock_data)

    sample_user_settings = tmp_path / "user_settings.json"
    sample_user_settings.write_text(
        json.dumps({"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "GOOGL"]}), encoding="utf-8"
    )

    excel_path = tmp_path / "operations.xlsx"
    sample_transactions.to_excel(excel_path, index=False)

    result = main(
        date_str="2021-12-31 12:00:00",
        excel_path=str(excel_path),
        user_settings_path=str(sample_user_settings),
        api_key="fake_api_key",
    )
    result_json = json.loads(result)

    assert result_json["greeting"] == "Добрый день"
    assert len(result_json["cards"]) == 3
    assert len(result_json["top_transactions"]) == 3
    assert len(result_json["currency_rates"]) == 2
    assert len(result_json["stock_prices"]) == 2
