import os
import sys
import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import patch

# Добавила src/ в sys.path, чтобы импорты точно работали
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from src.views import (
    get_greeting,
    get_card_stats,
    get_top_transactions,
    main_view,
    event_view,
)

# Путь к файлу
TEST_FILE = os.path.join("data", "operations.xlsx")


def test_get_greeting():
    assert get_greeting("2021-12-31 06:30:00") == "Доброе утро"
    assert get_greeting("2021-12-31 13:00:00") == "Добрый день"
    assert get_greeting("2021-12-31 19:30:00") == "Добрый вечер"
    assert get_greeting("2021-12-31 02:00:00") == "Доброй ночи"


def test_get_card_stats():
    data = {
        "Номер карты": ["*1111", "*1111", "*2222"],
        "Сумма платежа": [100.0, 200.0, 300.0]
    }
    df = pd.DataFrame(data)
    result = get_card_stats(df)

    assert len(result) == 2
    assert any(card["last_digits"] == "*1111" and card["total_spent"] == 300.0 for card in result)
    assert any(card["last_digits"] == "*2222" and card["cashback"] == 3.0 for card in result)


def test_get_top_transactions():
    data = {
        "Дата операции": [datetime(2021, 12, 30), datetime(2021, 12, 31)],
        "Сумма платежа": [1000.0, 500.0],
        "Категория": ["Пополнения", "Супермаркеты"],
        "Описание": ["Через банк", "Пятёрочка"]
    }
    df = pd.DataFrame(data)
    result = get_top_transactions(df, top_n=1)

    assert len(result) == 1
    assert result[0]["amount"] == 1000.0
    assert result[0]["category"] == "Пополнения"

# Тест main_view с mock API

@pytest.mark.skipif(
    not os.path.exists(TEST_FILE),
    reason="Файл data/operations.xlsx не найден"
)
@patch("src.views.get_currency_rates")
@patch("src.views.get_stock_prices")
def test_main_view_output(mock_stocks, mock_currencies):
    mock_stocks.return_value = [
        {"stock": "AAPL", "price": 150.0},
        {"stock": "GOOGL", "price": 2500.0}
    ]
    mock_currencies.return_value = [
        {"currency": "USD", "rate": 73.0},
        {"currency": "EUR", "rate": 86.0}
    ]

    result = main_view("2021-12-31 16:00:00", file_path=TEST_FILE)

    assert isinstance(result, dict)
    assert isinstance(result["greeting"], str)
    assert isinstance(result["cards"], list)
    assert isinstance(result["top_transactions"], list)
    assert result["currency_rates"] == mock_currencies.return_value
    assert result["stock_prices"] == mock_stocks.return_value

# Тест event_view с mock API

@pytest.mark.skipif(not os.path.exists(TEST_FILE), reason="Файл data/operations.xlsx не найден")
@patch("src.views.get_currency_rates")
@patch("src.views.get_stock_prices")
def test_event_view_output(mock_stocks, mock_rates):
    mock_rates.return_value = [{"currency": "USD", "rate": 1.1}, {"currency": "EUR", "rate": 1.0}]
    mock_stocks.return_value = [{"stock": "AAPL", "price": 250.0}, {"stock": "TSLA", "price": 300.0}]

    result = event_view("2021-12-31 16:00:00", file_path=TEST_FILE)

    assert isinstance(result, dict)
    assert "expenses" in result
    assert "income" in result
    assert "categories" in result
    assert "currency_rates" in result
    assert "stock_prices" in result

    assert isinstance(result["expenses"], float)
    assert isinstance(result["income"], float)
    assert isinstance(result["categories"], dict)
    assert isinstance(result["currency_rates"], list)
    assert isinstance(result["stock_prices"], list)

    assert result["currency_rates"] == mock_rates.return_value
    assert result["stock_prices"] == mock_stocks.return_value
