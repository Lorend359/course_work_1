from dotenv import load_dotenv
import os
import pandas as pd

from src.views import main as main_view
from src.services import search_transactions
from src.reports import spending_by_category

if __name__ == "__main__":
    # Загружаем переменные окружения
    load_dotenv()
    api_key = os.getenv("API_KEY")

    # Выполнение сценария главной страницы
    date_str = "2021-12-31 12:00:00"
    result_main = main_view(
        date_str=date_str,
        excel_path="data/operations.xlsx",
        user_settings_path="user_settings.json",
        api_key=api_key,
    )
    print("Результат главной страницы:\n", result_main)

    # Выполнение поиска транзакций по запросу
    query_str = "Колхоз"
    result_search = search_transactions(
        query=query_str,
        excel_path="data/operations.xlsx",
    )
    print(f"\nРезультат поиска по '{query_str}':\n", result_search)

    # Генерация отчета "Траты по категории"
    df = pd.read_excel("data/operations.xlsx")
    filtered_df = spending_by_category(
        transactions=df,
        category="Супермаркеты",
        date="2021-12-31"
    )
    print("\nРезультат отчета 'Траты по категории':")
    print(filtered_df.head())
