import datetime
import logging
import os
from typing import Callable, Optional, Any

import pandas as pd


def default_report_decorator(func: Callable[..., pd.DataFrame]) -> Callable[..., pd.DataFrame]:
    """
    Декоратор сохраняет результат функции в JSON-файл с именем по умолчанию в директорию 'reports'.
    """
    def wrapper(*args: Any, **kwargs: Any) -> pd.DataFrame:
        df_result = func(*args, **kwargs)
        result_json = df_result.to_json(orient="records", force_ascii=False)
        timestamp = int(datetime.datetime.now().timestamp())
        filename = f"report_{timestamp}.json"
        filepath = os.path.join("reports", filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(result_json)

        logging.info(f"Report saved to {filepath}")
        return df_result

    return wrapper


def param_report_decorator(filename: str) -> Callable[[Callable[..., pd.DataFrame]], Callable[..., pd.DataFrame]]:
    """
    Декоратор сохраняет результат функции в указанный JSON-файл в директорию 'reports'.
    """
    def real_decorator(func: Callable[..., pd.DataFrame]) -> Callable[..., pd.DataFrame]:
        def wrapper(*args: Any, **kwargs: Any) -> pd.DataFrame:
            df_result = func(*args, **kwargs)
            result_json = df_result.to_json(orient="records", force_ascii=False)
            filepath = os.path.join("reports", filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(result_json)

            logging.info(f"Report saved to {filepath}")
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
    end_date: datetime.datetime = pd.to_datetime(date) if date else datetime.datetime.now()
    start_date: datetime.datetime = end_date - pd.DateOffset(months=3)

    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True, errors="coerce")

    filtered: pd.DataFrame = transactions[
        (transactions["Категория"] == category)
        & (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= end_date)
    ]

    logging.info(f"{len(filtered)} rows found for category '{category}'.")
    return filtered
