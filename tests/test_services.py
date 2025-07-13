from src.services import (
    analyze_cashback_categories,
    investment_bank,
    simple_search,
    find_phone_transactions,
    find_personal_transfers,
)

# Пример транзакций для тестов
sample_data = [
    {
        "Дата операции": "2021-12-10",
        "Сумма операции": -1000.0,
        "Категория": "Супермаркеты",
        "Описание": "Пятёрочка",
    },
    {
        "Дата операции": "2021-12-11",
        "Сумма операция": -200.0,
        "Категория": "Связь",
        "Описание": "МТС Mobile +7 981 333-44-55",
    },
    {
        "Дата операция": "2021-12-15",
        "Сумма операция": -500.0,
        "Категория": "Переводы",
        "Описание": "Иван С.",
    },
    {
        "Дата операция": "2021-12-20",
        "Сумма операция": 3000.0,
        "Категория": "Пополнения",
        "Описание": "Пополнение через банкомат",
    },
]


def test_analyze_cashback_categories():
    result = analyze_cashback_categories(sample_data, 2021, 12)
    assert result["Супермаркеты"] == 50.0  # 5% от 1000


def test_investment_bank():
    result = investment_bank("2021-12", sample_data, limit=100)
    # Трат: 1000, 200, 500 → округления: 1000→1000, 200→200, 500→500, всего saved = 0
    assert result == 0.0


def test_simple_search_found():
    result = simple_search("пятёрочка", sample_data)
    assert len(result) == 1
    assert "Пятёрочка" in result[0]["Описание"]


def test_simple_search_not_found():
    result = simple_search("автомойка", sample_data)
    assert result == []


def test_find_phone_transactions():
    result = find_phone_transactions(sample_data)
    assert len(result) == 1
    assert "+7 981 333-44-55" in result[0]["Описание"]


def test_find_personal_transfers():
    result = find_personal_transfers(sample_data)
    assert len(result) == 1
    assert result[0]["Описание"] == "Иван С."
