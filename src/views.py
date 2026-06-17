import json
import logging
from datetime import datetime, timedelta

import pandas as pd
import requests

# Инициализируем логгер для этого файла
logger = logging.getLogger("views")


def get_greeting() -> str:
    """Возвращает приветствие в зависимости от текущего времени суток."""
    current_hour = datetime.now().hour
    if 6 <= current_hour < 12:
        return "Доброе утро"
    elif 12 <= current_hour < 18:
        return "Добрый день"
    elif 18 <= current_hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_currency_rates() -> list:
    """Получает курсы валют (USD, EUR) к рублю через API ЦБ РФ. Без заглушек."""
    try:
        response = requests.get("https://cbr-xml-daily.ru", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [
                {"currency": "USD", "rate": float(round(data["Valute"]["USD"]["Value"], 2))},
                {"currency": "EUR", "rate": float(round(data["Valute"]["EUR"]["Value"], 2))},
            ]
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка получения курсов валют через API: {e}")

    return []


def get_stock_prices() -> list:
    """Получает актуальные цены акций S&P 500 через бесплатный API. Без заглушек."""
    stocks_data = []
    tickers = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
    try:
        for ticker in tickers:
            response = requests.get(f"https://yahoo.com{ticker}", timeout=3)
            if response.status_code == 200:
                data = response.json()
                price = data["chart"]["result"]["meta"]["regularMarketPrice"]
                stocks_data.append({"stock": ticker, "price": float(round(price, 2))})
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка получения стоимости акций через API: {e}")

    return stocks_data


def get_events_page(df: pd.DataFrame, date_str: str, range_type: str = "M") -> str:
    """Генерирует JSON-ответ для страницы 'События' по ТЗ."""
    if df.empty:
        return json.dumps({})

    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)

    try:
        target_date = pd.to_datetime(date_str, dayfirst=True)
    except (ValueError, TypeError):
        target_date = pd.to_datetime(date_str)

    end_date = target_date
    if range_type == "W":
        start_date = end_date - timedelta(days=7)
    elif range_type == "M":
        start_date = end_date.replace(day=1)
    elif range_type == "Y":
        start_date = end_date.replace(month=1, day=1)
    else:
        start_date = df["Дата операции"].min()

    filtered_df = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)].copy()

    # Топ-5 транзакций по сумме
    filtered_df["abs_amount"] = filtered_df["Сумма операции"].abs()
    top_transactions_df = filtered_df.sort_values(by="abs_amount", ascending=False).head(5)

    transactions_list = []
    for _, row in top_transactions_df.iterrows():
        transactions_list.append(
            {
                "date": row["Дата операции"].strftime("%d.%m.%Y"),
                "amount": float(row["Сумма операции"]),
                "category": str(row["Категория"]),
                "description": str(row["Описание"]) if "Описание" in df.columns else str(row.get("Категория", "")),
            }
        )

    # Блок «Расходы» и «Поступления»
    expenses_df = filtered_df[filtered_df["Сумма операции"] < 0].copy()
    expenses_df["Сумма операции"] = expenses_df["Сумма операции"].abs()
    income_df = filtered_df[filtered_df["Сумма операции"] > 0].copy()

    total_expenses = int(round(expenses_df["Сумма операции"].sum())) if not expenses_df.empty else 0
    total_income = int(round(income_df["Сумма операции"].sum())) if not income_df.empty else 0

    main_expenses_list = []
    transfers_and_cash_list = []

    if not expenses_df.empty:
        cash_categories = ["Наличные", "Переводы"]
        transfers_data = expenses_df[expenses_df["Категория"].isin(cash_categories)]
        main_data = expenses_df[~expenses_df["Категория"].isin(cash_categories)]

        if not main_data.empty:
            main_grouped = main_data.groupby("Категория")["Сумма операции"].sum().reset_index()
            main_grouped = main_grouped.sort_values(by="Сумма операции", ascending=False)

            if len(main_grouped) > 7:
                top_7 = main_grouped.head(7)
                others_sum = main_grouped.iloc[7:]["Сумма операции"].sum()
                others_df = pd.DataFrame([{"Категория": "Остальное", "Сумма операции": others_sum}])
                main_grouped = pd.concat([top_7, others_df], ignore_index=True)

            main_expenses_list = [
                {"category": str(row["Категория"]), "amount": int(round(row["Сумма операции"]))}
                for _, row in main_grouped.iterrows()
            ]

        if not transfers_data.empty:
            transfers_grouped = transfers_data.groupby("Категория")["Сумма операции"].sum().reset_index()
            transfers_grouped = transfers_grouped.sort_values(by="Сумма операции", ascending=False)
            transfers_and_cash_list = [
                {"category": str(row["Категория"]), "amount": int(round(row["Сумма операции"]))}
                for _, row in transfers_grouped.iterrows()
            ]

    main_income_list = []
    if not income_df.empty:
        income_grouped = income_df.groupby("Категория")["Сумма операции"].sum().reset_index()
        income_grouped = income_grouped.sort_values(by="Сумма операции", ascending=False)
        main_income_list = [
            {"category": str(row["Категория"]), "amount": int(round(row["Сумма операции"]))}
            for _, row in income_grouped.iterrows()
        ]

    response_data = {
        "greeting": get_greeting(),
        "top_transactions": transactions_list,
        "expenses": {
            "total_amount": total_expenses,
            "main": main_expenses_list,
            "transfers_and_cash": transfers_and_cash_list,
        },
        "income": {"total_amount": total_income, "main": main_income_list},
        "currency_rates": get_currency_rates(),
        "stock_prices": get_stock_prices(),
    }

    return json.dumps(response_data, ensure_ascii=False, indent=2)
