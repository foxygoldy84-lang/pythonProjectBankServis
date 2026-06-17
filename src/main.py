import json
import logging
import os

import pandas as pd

import src.reports as reports
import src.services as services
import src.utils as utils
import src.views as views

logger = logging.getLogger("main")


def main() -> None:
    logger.info("Запуск банковского приложения")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "operations.xlsx")

    print("==================================================")
    print(" ЧТЕНИЕ ДАННЫХ ИЗ EXCEL")
    print("==================================================")
    df = utils.read_transactions_dataframe(data_path)
    transactions_list = utils.read_transactions_xlsx(data_path)

    if df.empty:
        print(f"⚠️ Внимание! Файл не найден или пуст по пути: {data_path}")
        return

    print(f"Успешно загружено транзакций для анализа: {len(df)}")

    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    latest_date_obj = df["Дата операции"].max()
    test_date = latest_date_obj.strftime("%d.%m.%Y")
    test_month = latest_date_obj.strftime("%Y-%m")

    print(f"Анализ проводится по самой свежей контрольной дате файла: {test_date}\n")

    print("==================================================")
    print(" 1. СТРАНИЦА 'СОБЫТИЯ' (модуль views.py)")
    print("==================================================")
    events_json = views.get_events_page(df, date_str=test_date, range_type="M")
    print(events_json)
    print()

    print("==================================================")
    print(" 2. СЕРВИС 'ИНВЕСТКОПИЛКА' (модуль services.py)")
    print("==================================================")
    limit_step = 50
    saved_money = services.investment_bank(month=test_month, transactions=transactions_list, limit=limit_step)
    print(f"Статистика за целевой месяц: {test_month}")
    print(f"В копилку отложено: {saved_money} руб.\n")

    print("==================================================")
    print(" 3. СЕРВИС 'ПРОСТОЙ ПОИСК' (вывод результатов)")
    print("==================================================")
    search_query = "Супермаркеты"
    search_results = services.process_bank_search(transactions_list, search_query)
    print(f"Результаты поиска по ключевому слову '{search_query}':")
    print(json.dumps(search_results[:5], ensure_ascii=False, indent=2))
    print(f"\nВсего найдено и возвращено транзакций: {len(search_results)}\n")

    print("==================================================")
    print(" 4. ОТЧЕТ 'ТРАТЫ ПО ДНЯМ НЕДЕЛИ' (модуль reports.py)")
    print("==================================================")
    report_df = reports.spending_by_weekday(df, date=test_date)
    print(report_df.to_string(index=False))
    print("\n* Декоратор автоматически сохранил этот отчет в файл 'spending_by_weekday.csv' *")
    print("==================================================")


if __name__ == "__main__":
    main()
