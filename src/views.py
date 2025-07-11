import os
import json
from datetime import datetime
from typing import Any

from src.utils import (
    load_operations,
    filter_by_date,
    get_currency_rates,
    get_stock_prices
)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(CURRENT_DIR, "..", "user_settings.json")
DATA_PATH = os.path.join(CURRENT_DIR, "..", "data", "operations.xlsx")


def get_greeting(date_str: str) -> str:
    """
    Возвращает приветствие в зависимости от времени суток.
    """
    time = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").time()
    if 5 <= time.hour < 12:
        return "Доброе утро"
    elif 12 <= time.hour < 17:
        return "Добрый день"
    elif 17 <= time.hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_card_stats(df) -> list[dict]:
    """
    Возвращает список словарей с информацией по каждой карте:
    последние цифры, общая сумма, кешбэк.
    """
    grouped = df.groupby("Номер карты")["Сумма платежа"].sum().reset_index()

    result = []
    for _, row in grouped.iterrows():
        last_digits = str(row["Номер карты"])
        total_spent = round(row["Сумма платежа"], 2)
        cashback = round(total_spent / 100, 2)

        result.append({
            "last_digits": last_digits,
            "total_spent": total_spent,
            "cashback": cashback
        })

    return result


def get_top_transactions(df, top_n=5) -> list[dict]:
    """
    Возвращает топ-N транзакций по убыванию суммы платежа.
    """
    df_sorted = df.sort_values(by="Сумма платежа", ascending=False).head(top_n)

    result = []
    for _, row in df_sorted.iterrows():
        result.append({
            "date": row["Дата операции"].strftime("%d.%m.%Y"),
            "amount": round(row["Сумма платежа"], 2),
            "category": row["Категория"],
            "description": row["Описание"]
        })

    return result


def main_view(input_date: str, file_path: str = DATA_PATH, settings_path: str = SETTINGS_PATH) -> dict[str, Any]:
    """
    Основная функция: собирает все данные в итоговый JSON для страницы "Главная".
    """
    df = load_operations(file_path)
    filtered_df = filter_by_date(df, input_date)
    greeting = get_greeting(input_date)

    cards = get_card_stats(filtered_df)
    top_tx = get_top_transactions(filtered_df)

    with open(settings_path, encoding="utf-8") as f:
        settings = json.load(f)

    currencies = settings.get("user_currencies", [])
    stocks = settings.get("user_stocks", [])

    currency_rates = get_currency_rates(currencies)
    stock_prices = get_stock_prices(stocks)

    return {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_tx,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }


def event_view(date_str: str, file_path: str = DATA_PATH, settings_path: str = SETTINGS_PATH) -> dict:
    """
    Формирует данные для страницы "События".
    """
    df = load_operations(file_path)
    df_filtered = filter_by_date(df, date_str)

    expenses = float(df_filtered[df_filtered["Сумма платежа"] < 0]["Сумма платежа"].sum())
    income = float(df_filtered[df_filtered["Сумма платежа"] > 0]["Сумма платежа"].sum())

    def filter_categories(dataframe, keyword):
        return dataframe[dataframe["Категория"].str.lower().str.contains(keyword)]

    categories = {
        "main": df_filtered[
            ~df_filtered["Категория"].str.lower().str.contains("перевод|налич")
        ]["Категория"].unique().tolist(),
        "transfers": filter_categories(df_filtered, "перевод")["Категория"].unique().tolist(),
        "cash": filter_categories(df_filtered, "налич")["Категория"].unique().tolist(),
    }

    with open(settings_path, encoding="utf-8") as f:
        settings = json.load(f)

    currency_rates = get_currency_rates(settings["user_currencies"])
    stock_prices = get_stock_prices(settings["user_stocks"])

    return {
        "expenses": round(expenses, 2),
        "income": round(income, 2),
        "categories": categories,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }
