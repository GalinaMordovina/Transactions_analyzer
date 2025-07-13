import os
import pandas as pd
import re
import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Callable


# Создаем директорию logs, если ее нет
os.makedirs("logs", exist_ok=True)

# Настройка логгирования в файл logs/activity.log
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/activity.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)


def save_report(func: Optional[Callable] = None, *, filename: Optional[str] = None):
    """
    Декоратор для сохранения результата функции-отчета в JSON-файл.
    Работает только если аргумент save_to_file=True
    """

    def decorator(inner_func):
        @wraps(inner_func)
        def wrapper(*args, **kwargs):
            result = inner_func(*args, **kwargs)
            if kwargs.get("save_to_file"):
                report_filename = filename or f"logs/report_{inner_func.__name__}.json"
                try:
                    with open(report_filename, "w", encoding="utf-8") as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    logging.info(f"Отчет сохранен в файл: {report_filename}")
                except Exception as e:
                    logging.error(f"Не удалось сохранить отчет: {e}")
            return result

        return wrapper

    if callable(func):
        return decorator(func)
    return decorator


@save_report
def spending_by_category(
    transactions: pd.DataFrame,
    category: str,
    date: Optional[str] = None,
    save_to_file: bool = False,
) -> list[dict]:
    """
    Возвращает траты по заданной категории за последние три месяца от указанной даты.
    """
    if date is None:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(date, "%Y-%m-%d")

    start_date = end_date - timedelta(days=90)

    df = transactions.copy()
    df["Дата операции"] = pd.to_datetime(
        df["Дата операции"], errors="coerce", dayfirst=True
    )
    df = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)]

    filtered = df[df["Категория"].astype(str).str.lower() == category.lower()]
    expenses = filtered[filtered["Сумма платежа"] < 0]

    result = [
        {
            "date": row["Дата операции"].strftime("%Y-%m-%d"),
            "amount": round(row["Сумма платежа"], 2),
            "description": row.get("Описание", ""),
        }
        for _, row in expenses.iterrows()
    ]

    logging.info(f"Найдено {len(result)} трат по категории '{category}' за 3 месяца")
    return result


@save_report
def spending_by_weekday(
    transactions: pd.DataFrame, date: Optional[str] = None, save_to_file: bool = False
) -> list[dict]:
    """
    Возвращает средние траты в каждый из дней недели за последние 3 месяца.
    """
    if date is None:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(date, "%Y-%m-%d")

    start_date = end_date - timedelta(days=90)

    df = transactions.copy()
    df["Дата операции"] = pd.to_datetime(
        df["Дата операции"], errors="coerce", dayfirst=True
    )
    df = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)]
    df = df[df["Сумма платежа"] < 0]

    df["weekday"] = df["Дата операции"].dt.day_name()
    result = (
        df.groupby("weekday")["Сумма платежа"]
        .mean()
        .apply(lambda x: round(x, 2))
        .reset_index()
        .rename(columns={"Сумма платежа": "average_spent"})
        .to_dict(orient="records")
    )

    logging.info("Сформирован отчет по средним тратам по дням недели")
    return result


@save_report
def spending_by_workday(
    transactions: pd.DataFrame, date: Optional[str] = None, save_to_file: bool = False
) -> dict[str, float]:
    """
    Возвращает средние траты в рабочий и выходной день за последние 3 месяца.
    """
    if date is None:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(date, "%Y-%m-%d")

    start_date = end_date - timedelta(days=90)

    df = transactions.copy()
    df["Дата операции"] = pd.to_datetime(
        df["Дата операции"], errors="coerce", dayfirst=True
    )
    df = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)]
    df = df[df["Сумма платежа"] < 0]

    df["is_workday"] = df["Дата операции"].dt.weekday < 5
    result = df.groupby("is_workday")["Сумма платежа"].mean().to_dict()

    final_result = {
        "workday_avg": round(result.get(True, 0.0), 2),
        "weekend_avg": round(result.get(False, 0.0), 2),
    }

    logging.info("Сформирован отчет по тратам в рабочие и выходные дни")
    return final_result


def convert_log_to_excel(
    log_file="logs/activity.log", output_file="logs/activity_report.xlsx"
) -> None:
    """
    Преобразует лог-файл в Excel-таблицу с колонками: Дата, Уровень, Сообщение
    """
    if not os.path.exists(log_file):
        print(f"[!] Лог-файл '{log_file}' не найден.")
        return

    pattern = re.compile(r"^(?P<date>[\d\-:\s]+) - (?P<level>\w+) - (?P<message>.+)$")
    records = []

    with open(log_file, encoding="utf-8") as f:
        for line in f:
            match = pattern.match(line.strip())
            if match:
                records.append(match.groupdict())

    if not records:
        print("[!] Лог пустой, нечего конвертировать.")
        return

    df = pd.DataFrame(records)
    df.to_excel(output_file, index=False)
    print(f"[✓] Отчет логов сохранен в '{output_file}'")
