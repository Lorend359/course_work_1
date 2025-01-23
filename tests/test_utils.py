import json

import pandas as pd
import pytest

from src.utils import fetch_currency_data, fetch_stock_data, filter_transactions_by_date, load_user_settings


@pytest.fixture
def sample_transactions():
    """
    Пример транзакций для тестов.
    """
    data = pd.DataFrame(
        {
            "Дата операции": ["01.12.2021 12:00:00", "15.12.2021 11:59:59", "31.12.2021 12:00:00"],
            "Сумма операции": [1000, 500, -200],
            "Кэшбэк": [10, 5, 0],
            "Номер карты": ["*1234", "*5678", "*9012"],
        }
    )
    return data


def test_filter_transactions_by_date(sample_transactions):
    """
    Проверяет фильтрацию транзакций по заданному диапазону дат.
    """
    filtered = filter_transactions_by_date(sample_transactions, "2021-12-31 12:00:00")
    assert len(filtered) == 3
    assert filtered.iloc[0]["Сумма операции"] == 1000
    assert filtered.iloc[1]["Сумма операции"] == 500
    assert filtered.iloc[2]["Сумма операции"] == -200


@pytest.fixture
def sample_user_settings(tmp_path):
    """
    Создает временный файл с пользовательскими настройками.
    """
    settings = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "GOOGL"]}
    file_path = tmp_path / "user_settings.json"
    file_path.write_text(json.dumps(settings), encoding="utf-8")
    return str(file_path)


def test_load_user_settings(sample_user_settings):
    """
    Проверяет загрузку пользовательских настроек из файла.
    """
    settings = load_user_settings(sample_user_settings)
    assert settings["user_currencies"] == ["USD", "EUR"]
    assert settings["user_stocks"] == ["AAPL", "GOOGL"]


@pytest.mark.parametrize(
    "mocked_response,expected",
    [
        ({"forexList": [{"ticker": "USD/EUR", "bid": "0.85"}]}, {"EUR": 0.85}),
        ({"forexList": [{"ticker": "USD/USD", "bid": "1.00"}]}, {"USD": 1.00}),
    ],
)
def test_fetch_currency_data(mocked_response, expected, monkeypatch):
    """
    Проверяет получение данных о курсах валют.
    """

    def mock_get(*args, **kwargs):
        class MockResponse:
            status_code = 200

            def json(self):
                return mocked_response

        return MockResponse()

    monkeypatch.setattr("requests.get", mock_get)
    result = fetch_currency_data("fake_api_key", list(expected.keys()))
    assert result == expected


@pytest.mark.parametrize(
    "mocked_response,expected",
    [
        ([{"symbol": "AAPL", "price": 150.00}], [{"stock": "AAPL", "price": 150.00}]),
        ([{"symbol": "GOOGL", "price": 2800.00}], [{"stock": "GOOGL", "price": 2800.00}]),
    ],
)
def test_fetch_stock_data(mocked_response, expected, monkeypatch):
    """
    Проверяет получение данных о ценах акций.
    """

    def mock_get(*args, **kwargs):
        class MockResponse:
            status_code = 200

            def json(self):
                return mocked_response

        return MockResponse()

    monkeypatch.setattr("requests.get", mock_get)
    result = fetch_stock_data("fake_api_key", [item["stock"] for item in expected])
    assert result == mocked_response
