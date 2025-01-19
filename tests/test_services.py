import json

import pandas as pd

from src.services import search_transactions


def test_search_transactions(tmp_path):
    """
    Тестирует поиск строк в колонках 'Описание' и 'Категория'.
    """
    df = pd.DataFrame(
        {
            "Дата операции": ["31.12.2021 10:00:00", "31.12.2021 16:44:00", "01.01.2022 00:00:00"],
            "Категория": ["Супермаркеты", "Супермаркеты", "Супермаркеты"],
            "Описание": ["Колхоз", "Магнит", "Колхоз-Двор"],
            "Сумма операции": [100, 200, 300],
        }
    )

    excel_path = tmp_path / "operations.xlsx"
    df.to_excel(excel_path, index=False)

    result_str = search_transactions(query="колхоз", excel_path=str(excel_path))
    result = json.loads(result_str)

    assert result["search_query"] == "колхоз"
    assert "results" in result
    assert result["count"] == 2
    assert len(result["results"]) == 2

    desc = [r["Описание"] for r in result["results"]]
    assert "Колхоз" in desc
    assert "Колхоз-Двор" in desc