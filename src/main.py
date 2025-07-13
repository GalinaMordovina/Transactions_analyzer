import json
import os
from dotenv import load_dotenv
from src.views import main_view, event_view
from src.services import simple_search, find_phone_transactions, find_personal_transfers
from src.utils import load_operations
from src.reports import (
    spending_by_category,
    spending_by_weekday,
    spending_by_workday,
    convert_log_to_excel,
)

load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_PATH = os.path.join(BASE_DIR, "data", "operations.xlsx")


if __name__ == "__main__":
    input_date = "2021-12-31 16:00:00"
    result = main_view(input_date)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    # Вызовем функцию и распечатаем результат event_view События
    print("\n=== События ===")
    event_data = event_view("2021-12-31 16:00:00")
    print(event_data)
    # Загружаем операции
    df = load_operations(FILE_PATH)
    transactions = df.to_dict(orient="records")

    # Простой поиск
    print("\n=== Простой поиск ===")
    use_search = input("Хотите выполнить простой поиск? (да/нет): ").strip().lower()
    if use_search in ("да", "д", "yes", "y"):
        query = (
            input("Введите слово для поиска в описании или категории: ").strip().lower()
        )
        search_results = simple_search(query, transactions)
        if search_results:
            print(json.dumps(search_results[:3], ensure_ascii=False, indent=2))
        else:
            print("Ничего не найдено по вашему запросу.")
    else:
        print("Простой поиск пропущен.")

    # Поиск по номерам телефонов
    print("\n=== Поиск по телефонным номерам ===")
    use_phone = (
        input("Хотите найти транзакции с номерами телефонов? (да/нет): ")
        .strip()
        .lower()
    )
    if use_phone in ("да", "д", "yes", "y"):
        phone_results = find_phone_transactions(transactions)
        if phone_results:
            print(json.dumps(phone_results[:3], ensure_ascii=False, indent=2))
        else:
            print("Номера телефонов не найдены.")
    else:
        print("Поиск по телефонам пропущен.")

    # Поиск переводов физическим лицам
    print("\n=== Поиск переводов физическим лицам ===")
    use_personal = (
        input("Хотите найти переводы физическим лицам? (да/нет): ").strip().lower()
    )
    if use_personal in ("да", "д", "yes", "y"):
        personal_results = find_personal_transfers(transactions)
        if personal_results:
            print(json.dumps(personal_results[:3], ensure_ascii=False, indent=2))
        else:
            print("Переводы физическим лицам не найдены.")
    else:
        print("Поиск переводов пропущен.")

    # Получение даты от пользователя
    date_input = input(
        "Введите дату (в формате YYYY-MM-DD) или нажмите Enter для текущей даты: "
    )
    date = date_input if date_input else None

    # Отчет по категории
    category = input(
        "Сформировать отчет по категории? (введите категорию или оставьте пустым): "
    )
    if category:
        print(f"\n=== Отчет: Траты по категории '{category}' ===")
        report = spending_by_category(df, category, date, save_to_file=False)
        print(json.dumps(report, ensure_ascii=False, indent=2))

    # Отчет по дням недели
    run_weekday = input("Сформировать отчет по дням недели? (да/нет): ").strip().lower()
    if run_weekday == "да":
        print("\n=== Отчет: Средние траты по дням недели ===")
        report = spending_by_weekday(df, date, save_to_file=False)
        print(json.dumps(report, ensure_ascii=False, indent=2))

    # Отчет по рабочим/выходным дням
    run_workday = (
        input("Сформировать отчет по типу дня (рабочий/выходной)? (да/нет): ")
        .strip()
        .lower()
    )
    if run_workday == "да":
        print("\n=== Отчет: Средние траты по типу дня ===")
        report = spending_by_workday(df, date, save_to_file=False)
        print(json.dumps(report, ensure_ascii=False, indent=2))

    convert_log_to_excel()
