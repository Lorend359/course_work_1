from dotenv import load_dotenv
import os

import pandas as pd

from src.views import main as main_view
from src.services import search_transactions
from src.reports import spending_by_category

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("API_KEY")

    # 1) Запускаем "Главную страницу"
    date_str = "2021-12-31 12:00:00"
    result_main = main_view(
        date_str=date_str,
        excel_path="data/operations.xlsx",
        user_settings_path="user_settings.json",
        api_key=api_key,
    )
    print("Результат главной страницы:\n", result_main)

    # 2) Запускаем "Простой поиск"
    query_str = "Колхоз"
    result_search = search_transactions(
        query=query_str,
        excel_path="data/operations.xlsx",
    )
    print(f"\nРезультат поиска по '{query_str}':\n", result_search)

    # 3) Читаем Excel как DataFrame и вызываем spending_by_category
    df = pd.read_excel("data/operations.xlsx")
    # Например, берем категорию "Супермаркеты", и дату "2021-12-31"
    # Декоратор автоматом сохранит результат в report_*.json
    filtered_df = spending_by_category(df, "Супермаркеты", "2021-12-31")
    print("\nРезультат отчета 'Траты по категории':")
    print(filtered_df.head())
