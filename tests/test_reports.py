import json
import os

import pandas as pd

from src.reports import default_report_decorator, param_report_decorator, spending_by_category


def test_spending_by_category():
    """
    Проверяет фильтрацию транзакций по категории и за последние три месяца от указанной даты.
    """
    data = pd.DataFrame(
        {
            "Дата операции": [
                "2022-12-01 10:00:00",
                "2022-10-15 12:00:00",
                "2022-09-01 23:59:59",
                "2022-08-31 11:59:59",
            ],
            "Категория": ["Супермаркеты", "Супермаркеты", "Оплата", "Супермаркеты"],
            "Сумма операции": [100, 500, -200, 999],
        }
    )
    filtered = spending_by_category(data, category="Супермаркеты", date="2022-12-31")
    assert len(filtered) == 2
    assert all(filtered["Категория"] == "Супермаркеты")


@default_report_decorator
def dummy_report_default(df: pd.DataFrame) -> pd.DataFrame:
    """
    Тестовая функция для default_report_decorator.
    """
    return df


def test_default_decorator(tmp_path):
    """
    Проверяет сохранение JSON-файла с помощью default_report_decorator.
    """
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    current_dir = os.getcwd()
    os.chdir(tmp_path)
    try:
        result_df = dummy_report_default(df)
        assert result_df.equals(df)
        files = list(tmp_path.iterdir())
        assert len(files) == 1
        report_file = files[0]
        assert report_file.name.startswith("report_")
        assert report_file.suffix == ".json"
        content = report_file.read_text(encoding="utf-8")
        data = json.loads(content)
        assert len(data) == 2
        assert data[0]["A"] == 1
        assert data[1]["B"] == 4
    finally:
        os.chdir(current_dir)


@param_report_decorator("my_custom_report.json")
def dummy_report_param(df: pd.DataFrame) -> pd.DataFrame:
    """
    Тестовая функция для param_report_decorator.
    """
    return df


def test_param_decorator(tmp_path):
    """
    Проверяет сохранение JSON-файла с помощью param_report_decorator.
    """
    df = pd.DataFrame({"X": [10, 20], "Y": [30, 40]})
    current_dir = os.getcwd()
    os.chdir(tmp_path)
    try:
        result_df = dummy_report_param(df)
        assert result_df.equals(df)
        report_file = tmp_path / "my_custom_report.json"
        assert report_file.exists()
        content = report_file.read_text(encoding="utf-8")
        data = json.loads(content)
        assert len(data) == 2
        assert data[0]["X"] == 10
        assert data[1]["Y"] == 40
    finally:
        os.chdir(current_dir)
