import datetime
import logging
from typing import Optional

import pandas as pd


def default_report_decorator(func):
    """
    Декоратор сохраняет результат функции в JSON-файл с именем по умолчанию.
    """

    def wrapper(*args, **kwargs):
        df_result = func(*args, **kwargs)
        result_json = df_result.to_json(orient="records", force_ascii=False)
        timestamp = int(datetime.datetime.now().timestamp())
        filename = f"report_{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(result_json)

        logging.info(f"Report saved to {filename}")
        return df_result

    return wrapper


def param_report_decorator(filename):
    """
    Декоратор сохраняет результат функции в указанный JSON-файл.
    """

    def real_decorator(func):
        def wrapper(*args, **kwargs):
            df_result = func(*args, **kwargs)
            result_json = df_result.to_json(orient="records", force_ascii=False)

            with open(filename, "w", encoding="utf-8") as f:
                f.write(result_json)

            logging.info(f"Report saved to {filename}")
            return df_result

        return wrapper

    return real_decorator


@default_report_decorator
def spending_by_category(
    transactions: pd.DataFrame,
    category: str,
    date: Optional[str] = None,
) -> pd.DataFrame:
    """
    Возвращает траты по заданной категории за последние три месяца.
    """
    end_date = pd.to_datetime(date) if date else datetime.datetime.now()
    start_date = end_date - pd.DateOffset(months=3)

    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True, errors="coerce")

    filtered = transactions[
        (transactions["Категория"] == category)
        & (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= end_date)
    ]

    logging.info(f"{len(filtered)} rows found for category '{category}'.")
    return filtered
