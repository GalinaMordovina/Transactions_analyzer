# Transactions Analyzer

Анализатор финансовых транзакций: загружает данные из Excel-файла, фильтрует и группирует операции, строит отчёты и сохраняет их в лог-файлы и Excel-формате.

## Возможности

-  Загрузка и парсинг Excel- и JSON-файлов с транзакциями
-  Поиск по ключевым словам, телефонам, физическим лицам
-  Формирование отчётов:
   - По категориям трат
   - По дням недели
   - По рабочим/выходным дням
-  Сохранение логов в Excel-файл
-  Покрытие тестами (>90%)
-  Гибкая структура проекта с использованием `Poetry`, `pytest`, `pandas`

---

## Быстрый старт

1. **Запустите приложение:**
```bash
poetry run python src/main.py
```

2. **Запустите тесты:**
```bash
poetry run pytest --cov=src
```

## Структура проекта
```bash
├── src/
│   ├── main.py               # Точка входа
│   ├── utils.py              # Работа с файлами и форматами
│   ├── services.py           # Поисковые функции
│   ├── reports.py            # Отчеты и декоратор сохранения
│   ├── views.py              # Представления для веб-страниц
│   └── __init__.py           # Преобразование логов в Excel
├── tests/                    # Pytest-тесты
│   ├── test_reports.py
│   ├── test_services.py
│   ├── test_utils.py
│   ├── test_views.py
│   └── ...
├── data/
│   └── operations.xlsx       # Excel-файл с операциями
├── logs/
│   ├── activity.log          # Журнал логов
│   └── activity_report.xlsx  # Отчет логов
├── user_settings.json        # Пользовательские настройки
├── .env                      # Переменные окружения
├── .gitignore
├── pyproject.toml
├── README.md                 # Описание проекта
```
## Используемые технологии

- Python 3.12
- pandas
- pytest + pytest-cov
- logging
- re, json, datetime
- poetry

## Примеры использования

1. **Пример: Отчет по категории**
```bash
Введите категорию: Супермаркеты
=== Отчет: Траты по категории 'Супермаркеты' ===
[
  {
    "date": "2024-12-01",
    "amount": -400.0,
    "description": "Перекресток"
  },
  {
    "date": "2024-12-02",
    "amount": -500.0,
    "description": "Metro"
  },
  ...
]
```

2. **Отчет по дням недели**
```bash
=== Отчет: Средние траты по дням недели ===
[
  {"weekday": "Monday", "average_spent": -1250.50},
  {"weekday": "Wednesday", "average_spent": -870.00}
]
```
## Автор

[Galina Mordovina](https://github.com/GalinaMordovina)  
glukoloid@gmail.com