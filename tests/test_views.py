import pytest
from unittest.mock import patch, MagicMock
from src.views import (
    load_user_settings,
    fetch_stock_data,
    fetch_market_data,
    get_data_for_date,
    fetch_currency_data
)

# Тест для загрузки пользовательских настроек
@patch("builtins.open", new_callable=MagicMock)
def test_load_user_settings(mock_open):
    mock_file = MagicMock()
    mock_file.read.return_value = '{"user_stocks": ["AAPL", "GOOGL"], "user_currencies": ["USD", "EUR"]}'
    mock_open.return_value.__enter__.return_value = mock_file

    settings = load_user_settings('user_settings.json')
    assert settings == {"user_stocks": ["AAPL", "GOOGL"], "user_currencies": ["USD", "EUR"]}

# Тест для успешного получения данных об акциях
@patch("requests.get")
def test_fetch_stock_data_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"historicalStockList": []}
    mock_get.return_value = mock_response

    result = fetch_stock_data("AAPL", "2022-06-01", "2022-06-30")
    assert result == {"historicalStockList": []}
    mock_get.assert_called_once()

# Тест для обработки статуса 401 в fetch_stock_data
@patch("requests.get")
def test_fetch_stock_data_unauthorized(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_get.return_value = mock_response

    with pytest.raises(Exception) as excinfo:
        fetch_stock_data("AAPL", "2022-06-01", "2022-06-30")

    assert str(excinfo.value) == "Unauthorized access. Check your API key."

# Тест для обработки других ошибок в fetch_stock_data
@patch("requests.get")
def test_fetch_stock_data_other_error(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    with pytest.raises(Exception) as excinfo:
        fetch_stock_data("AAPL", "2022-06-01", "2022-06-30")

    assert str(excinfo.value) == "Error fetching data for AAPL: 500"

# Тест для получения данных о валюте
@patch("requests.get")
def test_fetch_currency_data(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"symbol": "USD", "price": 1.0},
        {"symbol": "EUR", "price": 0.85}
    ]
    mock_get.return_value = mock_response

    result = fetch_currency_data(["USD", "EUR"])
    assert result == [
        {"symbol": "USD", "price": 1.0},
        {"symbol": "EUR", "price": 0.85}
    ]
    mock_get.assert_called_once()

# Тест для обработки статуса 401 в fetch_currency_data
def test_fetch_currency_data_unauthorized():
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        with pytest.raises(Exception) as excinfo:
            fetch_currency_data(["USD", "EUR"])

        assert str(excinfo.value) == "Unauthorized access. Check your API key."

# Тест для обработки других ошибок в fetch_currency_data
def test_fetch_currency_data_other_error():
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(Exception) as excinfo:
            fetch_currency_data(["USD", "EUR"])

        assert str(excinfo.value) == "Error fetching currency data: 500"

# Тест для получения данных о рынке
@patch("src.views.fetch_stock_data")
@patch("src.views.fetch_currency_data")
@patch("src.views.load_user_settings")
def test_fetch_market_data(mock_load_user_settings, mock_fetch_currency_data, mock_fetch_stock_data):
    mock_load_user_settings.return_value = {"user_stocks": ["AAPL"], "user_currencies": ["USD"]}
    mock_fetch_stock_data.return_value = {
        "historicalStockList": [
            {
                "symbol": "AAPL",
                "historical": [{"date": "2022-06-01", "price": 150}]
            }
        ]
    }
    mock_fetch_currency_data.return_value = [
        {"symbol": "USD", "price": 1.0}
    ]

    result = fetch_market_data("22.06.2022")
    expected = {
        "AAPL": [{"date": "2022-06-01", "price": 150}],
        "currency_rates": {"USD": 1.0}
    }
    assert result == expected

# Тест для получения данных за определенную дату
@patch("src.views.fetch_market_data")
def test_get_data_for_date(mock_fetch_market_data):
    mock_fetch_market_data.return_value = {
        "AAPL": [{"date": "2022-06-01", "price": 150}]
    }

    result = get_data_for_date("22.06.2022")
    expected = {
        "AAPL": [{"date": "2022-06-01", "price": 150}]
    }
    assert result == expected

# Тест для обработки исключений в fetch_market_data
@patch("src.views.fetch_stock_data")
@patch("src.views.load_user_settings")
def test_fetch_market_data_exception(mock_load_user_settings, mock_fetch_stock_data, capsys):
    mock_load_user_settings.return_value = {"user_stocks": ["AAPL"]}
    mock_fetch_stock_data.side_effect = Exception("Error fetching stock data.")

    result = fetch_market_data("22.06.2022")

    assert result == {}

    captured = capsys.readouterr()
    assert "Error fetching stock data." in captured.out

# Тест для обработки общего исключения в fetch_stock_data
def test_fetch_stock_data_general_exception():
    with patch("requests.get") as mock_get:
        mock_get.side_effect = Exception("Something went wrong")

        with pytest.raises(Exception) as excinfo:
            fetch_stock_data("AAPL", "2022-06-01", "2022-06-30")

        assert str(excinfo.value) == "Something went wrong"

# Тест для проверки вывода исключения
def test_printing_exception(capsys):
    with patch("requests.get") as mock_get:
        mock_get.side_effect = Exception("Something went wrong")

        try:
            fetch_stock_data("AAPL", "2022-06-01", "2022-06-30")
        except Exception as e:
            print(e)

        captured = capsys.readouterr()
        assert "Something went wrong" in captured.out