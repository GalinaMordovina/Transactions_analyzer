import pandas as pd
from unittest.mock import patch
from src.utils import (
    load_operations,
    filter_by_date,
    get_currency_rates,
    get_stock_prices,
)


def test_load_operations():
    """
    Проверяет загрузку Excel-файла и наличие ожидаемых столбцов.
    """
    df = load_operations("data/operations.xlsx")
    assert not df.empty
    assert "Дата операции" in df.columns
    assert "Сумма платежа" in df.columns


def test_filter_by_date():
    """
    Проверяет фильтрацию по дате: данные с начала месяца до указанной даты.
    """
    df = pd.DataFrame(
        {
            "Дата операции": ["01.12.2021", "15.12.2021", "31.12.2021", "01.01.2022"],
            "Сумма платежа": [100, 200, 300, 400],
        }
    )
    result = filter_by_date(df, "2021-12-31")
    assert len(result) == 3
    assert result["Сумма платежа"].sum() == 600


@patch("src.utils.requests.get")
def test_get_currency_rates(mock_get):
    """
    Мокаем API-запрос и проверяем корректность получения валютных курсов.
    """
    mock_response = {"rates": {"USD": 1.1, "EUR": 1.0}}
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    result = get_currency_rates(["USD", "EUR"])
    assert isinstance(result, list)
    assert any(rate["currency"] == "USD" and rate["rate"] == 1.1 for rate in result)
    assert any(rate["currency"] == "EUR" and rate["rate"] == 1.0 for rate in result)


def test_get_stock_prices():
    """
    Проверяет возвращение подставных данных о стоимости акций.
    """
    stocks = ["AAPL", "TSLA"]
    result = get_stock_prices(stocks)
    assert isinstance(result, list)
    assert any(stock["stock"] == "AAPL" for stock in result)
    assert any(stock["stock"] == "TSLA" for stock in result)
