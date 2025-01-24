import json
import logging
from typing import List, Dict, Any

import pandas as pd


def search_transactions(query: str, excel_path: str = "data/operations.xlsx") -> str:
    """
    Выполняет поиск транзакций по строке запроса в указанных столбцах.
    """
    try:
        df: pd.DataFrame = pd.read_excel(excel_path)

        # Заполнение пропусков
        df["Описание"] = df["Описание"].fillna("")
        df["Категория"] = df["Категория"].fillna("")

        # Фильтрация строк по запросу
        mask: pd.Series = (
            df["Описание"].str.contains(query, case=False, na=False)
            | df["Категория"].str.contains(query, case=False, na=False)
        )
        filtered: pd.DataFrame = df[mask]

        # Формирование результата
        columns: List[str] = ["Дата операции", "Категория", "Описание", "Сумма операции"]
        results: List[Dict[str, Any]] = [
            {
                "Дата операции": str(row["Дата операции"]),
                "Категория": row["Категория"],
                "Описание": row["Описание"],
                "Сумма операции": row["Сумма операции"],
            }
            for row in filtered[columns].to_dict("records")
        ]

        response: Dict[str, Any] = {
            "search_query": query,
            "count": len(results),
            "results": results,
        }

        logging.info(f"Простой поиск '{query}' — найдено {len(results)} транзакций.")
        return json.dumps(response, ensure_ascii=False, indent=4)

    except Exception as e:
        logging.error(f"Ошибка при поиске: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False, indent=4)
