import json
import os

import pandas as pd

from src.reports import default_report_decorator, param_report_decorator, spending_by_category


def test_spending_by_category(tmp_path):
    """
    Проверяет фильтрацию транзакций по категории и за последние три месяца от указанной даты.
    """
    data = pd.DataFrame(
        {
            "Дата операции": [
                "01.12.2022 10:00:00",
                "15.10.2022 12:00:00",
                "01.09.2022 23:59:59",
                "31.08.2022 11:59:59",
            ],
            "Категория": ["Супермаркеты", "Супермаркеты", "Оплата", "Супермаркеты"],
            "Сумма операции": [100, 500, -200, 999],
        }
    )
    current_dir = os.getcwd()
    os.chdir(tmp_path)
    try:
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()

        filtered = spending_by_category(data, category="Супермаркеты", date="2022-12-31")
        assert len(filtered) == 2, f"Ожидалось 2 транзакции, получено {len(filtered)}"
        assert all(filtered["Категория"] == "Супермаркеты"), "Не все транзакции относятся к категории 'Супермаркеты'"

        report_files = list(reports_dir.glob("report_*.json"))
        assert len(report_files) == 1, f"Ожидалось 1 отчёт, найдено {len(report_files)}"
    finally:
        os.chdir(current_dir)


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
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()

        result_df = dummy_report_default(df)
        assert result_df.equals(df), "DataFrame не совпадает с ожидаемым результатом"

        report_files = list(reports_dir.glob("report_*.json"))
        assert len(report_files) == 1, f"Ожидалось 1 отчёт, найдено {len(report_files)}"

        report_file = report_files[0]
        assert report_file.name.startswith(
            "report_"
        ), f"Имя файла отчёта должно начинаться с 'report_', а получено {report_file.name}"
        assert (
            report_file.suffix == ".json"
        ), f"Файл отчёта должен иметь расширение '.json', а получено {report_file.suffix}"

        content = report_file.read_text(encoding="utf-8")
        data = json.loads(content)
        assert len(data) == 2, f"Ожидалось 2 записи в отчёте, найдено {len(data)}"
        assert data[0]["A"] == 1, "Значение 'A' первой записи некорректно"
        assert data[1]["B"] == 4, "Значение 'B' второй записи некорректно"
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
        reports_dir = tmp_path / "reports"
        reports_dir.mkdir()

        result_df = dummy_report_param(df)
        assert result_df.equals(df), "DataFrame не совпадает с ожидаемым результатом"

        report_file = reports_dir / "my_custom_report.json"
        assert report_file.exists(), f"Файл отчёта {report_file} не существует"

        content = report_file.read_text(encoding="utf-8")
        data = json.loads(content)
        assert len(data) == 2, f"Ожидалось 2 записи в отчёте, найдено {len(data)}"
        assert data[0]["X"] == 10, "Значение 'X' первой записи некорректно"
        assert data[1]["Y"] == 40, "Значение 'Y' второй записи некорректно"
    finally:
        os.chdir(current_dir)
