import pandas as pd
import os
import finnhub
import requests
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные из .env


def load_operations(file_path: str) -> pd.DataFrame:
    """
    Загружает Excel-файл с операциями и возвращает DataFrame.
    """
    return pd.read_excel(file_path)


def filter_by_date(df, end_date_str: str) -> pd.DataFrame:
    """
    Возвращает данные с начала месяца до переданной даты включительно.
    """
    df = df.copy()
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    end_date = pd.to_datetime(end_date_str)

    start_date = end_date.replace(day=1)
    return df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)]


def get_currency_rates(currencies: list[str]) -> list[dict]:
    """
    Получает курсы указанных валют через API и возвращает список словарей:
    [{"currency": "USD", "rate": 73.21}, ...]
    """
    api_key = os.getenv("API_KEY")
    base_url = os.getenv("API_URL")

    if not api_key or not base_url:
        raise ValueError("Переменные API_KEY или API_URL не найдены в .env")

    headers = {"apikey": api_key}

    response = requests.get(base_url, headers=headers)

    if response.status_code != 200:
        raise ValueError(f"Ошибка запроса: {response.status_code} - {response.text}")

    data = response.json()
    all_rates = data.get("rates", {})

    result = []
    for currency in currencies:
        rate = all_rates.get(currency)
        if rate is not None:
            result.append({"currency": currency, "rate": round(rate, 2)})

    return result


def get_stock_prices(stocks: list[str]) -> list[dict]:
    """
    Получает текущие цены указанных акций с помощью API Finnhub.
    """
    finnhub_key = os.getenv("FINNHUB_API_KEY")
    if not finnhub_key:
        raise ValueError("Переменная FINNHUB_API_KEY не найдена в .env")

    client = finnhub.Client(api_key=finnhub_key)
    results = []

    for stock in stocks:
        try:
            quote = client.quote(stock)
            price = quote.get("c")  # текущая цена
            if price:
                results.append({"stock": stock, "price": round(price, 2)})
        except Exception as e:
            results.append({"stock": stock, "price": 0.0})
            print(f"Ошибка при получении цены для {stock}: {e}")

    return results
