import logging
import re
from datetime import datetime
from collections import defaultdict
from typing import List, Dict


def analyze_cashback_categories(
    data: list[dict], year: int, month: int
) -> dict[str, float]:
    """
    Анализирует, сколько кешбэка можно получить по каждой категории.
    """
    logging.info(f"Анализ кэшбэка за {year}-{month:02d}")

    cashback_rate = 0.05  # 5% кэшбэк
    result = defaultdict(float)

    for tx in data:
        try:
            date = datetime.strptime(tx["Дата операции"], "%Y-%m-%d")
            if date.year == year and date.month == month:
                amount = float(tx["Сумма операции"])
                category = tx.get("Категория", "Неизвестно")
                if amount < 0:  # только расходы
                    result[category] += -amount * cashback_rate
        except Exception as e:
            logging.warning(f"Ошибка обработки транзакции: {tx} — {e}")

    return {k: round(v, 2) for k, v in result.items()}


def investment_bank(month: str, transactions: list[dict], limit: int) -> float:
    """
    Вычисляет сумму, которую можно отложить в инвесткопилку, округляя каждую трату.
    """
    total_saved = 0.0

    for tx in transactions:
        date_str = tx.get("Дата операции")
        amount = tx.get("Сумма операции")

        if not date_str or not isinstance(amount, (int, float)):
            continue

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue

        tx_month = date_obj.strftime("%Y-%m")

        # Только отрицательные суммы и нужный месяц
        if tx_month == month and amount < 0:
            rounded = ((-amount + limit - 1) // limit) * limit
            saved = rounded + amount  # amount отрицательное
            total_saved += saved

    logging.info(f"Инвесткопилка за {month}: {total_saved:.2f}")
    return round(total_saved, 2)


logging.basicConfig(level=logging.INFO)


def simple_search(query: str, transactions: list[dict]) -> list[dict]:
    """
    Возвращает транзакции, содержащие строку запроса в описании или категории.
    """
    query = query.lower()
    return [
        tx
        for tx in transactions
        if query in str(tx.get("Категория", "")).lower()
        or query in str(tx.get("Описание", "")).lower()
    ]


def find_phone_transactions(transactions: List[Dict]) -> List[Dict]:
    """
    Поиск транзакций с телефонными номерами в описании.
    """
    phone_pattern = re.compile(r"\+7\s?\d{3}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}")
    results = [
        tx for tx in transactions if phone_pattern.search(tx.get("Описание", ""))
    ]

    logging.info(f"Найдено {len(results)} транзакций с номерами телефонов.")
    return results


def find_personal_transfers(transactions: list[dict]) -> list[dict]:
    """
    Возвращает транзакции, которые относятся к переводам физлицам.
    Категория: 'Переводы', описание содержит имя и первую букву фамилии с точкой.
    Например: 'Сергей А.', 'Анна П.'
    """
    pattern = r"\b[А-ЯЁ][а-яё]+\s[А-ЯЁ]\."  # Пример: "Иван С."

    return [
        tx
        for tx in transactions
        if str(tx.get("Категория", "")).lower() == "переводы"
        and re.search(pattern, str(tx.get("Описание", "")))
    ]
