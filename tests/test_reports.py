import sys
import os
import pandas as pd
import pytest
from src.main import convert_log_to_excel


# Добавим src/ в sys.path, чтобы можно было импортировать модули
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from src.reports import (
    spending_by_category,
    spending_by_weekday,
    spending_by_workday,
    save_report
)


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "Дата операции": [
            "2024-10-01", "2024-10-02", "2024-10-03",
            "2024-11-01", "2024-11-02", "2024-11-03",
            "2024-12-01", "2024-12-02", "2024-12-03"
        ],
        "Сумма платежа": [-100, -200, -300, -400, -500, -600, -700, -800, -900],
        "Категория": [
            "Супермаркеты", "Супермаркеты", "Кафе",
            "Супермаркеты", "Кафе", "Супермаркеты",
            "Кафе", "Супермаркеты", "Супермаркеты"
        ],
        "Описание": [
            "Магнит", "Пятерочка", "Кофейня",
            "Перекресток", "Шоколадница", "Ашан",
            "Кофейня", "Metro", "FixPrice"
        ]
    })


def test_spending_by_category(sample_df):
    result = spending_by_category(sample_df, "Супермаркеты", "2024-12-01", save_to_file=False)
    assert isinstance(result, list)
    for row in result:
        assert "date" in row and "amount" in row and "description" in row
        assert row["amount"] < 0


def test_spending_by_weekday(sample_df):
    result = spending_by_weekday(sample_df, "2024-12-01", save_to_file=False)
    assert isinstance(result, list)
    for row in result:
        assert "weekday" in row and "average_spent" in row
        assert isinstance(row["average_spent"], float)


def test_spending_by_workday(sample_df):
    result = spending_by_workday(sample_df, "2024-12-01", save_to_file=False)
    assert isinstance(result, dict)
    assert "workday_avg" in result
    assert "weekend_avg" in result


def test_save_report_creates_file(tmp_path):
    @save_report(filename=str(tmp_path / "test_report.json"))
    def dummy_report(save_to_file=False):
        _ = save_to_file  # подавляет предупреждение линтера
        return {"example": 1}

    dummy_report(save_to_file=True)
    file_path = tmp_path / "test_report.json"
    assert file_path.exists()

    with open(file_path, encoding="utf-8") as f:
        data = f.read()
        assert '"example": 1' in data


def test_log_file_not_found(capsys, tmp_path):
    missing_log_path = tmp_path / "missing.log"
    output_file = tmp_path / "report.xlsx"

    convert_log_to_excel(str(missing_log_path), str(output_file))
    captured = capsys.readouterr()

    assert "[!] Лог-файл" in captured.out
    assert not output_file.exists()


def test_empty_log_file(capsys, tmp_path):
    log_file = tmp_path / "empty.log"
    log_file.write_text("", encoding="utf-8")
    output_file = tmp_path / "report.xlsx"

    convert_log_to_excel(str(log_file), str(output_file))
    captured = capsys.readouterr()

    assert "[!] Лог пустой" in captured.out
    assert not output_file.exists()


def test_convert_valid_log_to_excel(tmp_path):
    log_file = tmp_path / "test.log"
    output_file = tmp_path / "report.xlsx"

    log_file.write_text(
        "2025-07-10 10:00:00 - INFO - Отчет сформирован\n"
        "2025-07-10 10:05:00 - ERROR - Ошибка при сохранении файла\n",
        encoding="utf-8"
    )

    convert_log_to_excel(str(log_file), str(output_file))

    assert output_file.exists()

    df = pd.read_excel(output_file)
    assert len(df) == 2
    assert set(df.columns) == {"date", "level", "message"}
    assert df.iloc[0]["level"] == "INFO"
    assert "Отчет" in df.iloc[0]["message"]
