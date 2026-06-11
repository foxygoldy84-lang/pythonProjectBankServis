import json
from datetime import timedelta

import pandas as pd
import requests


def get_currency_rates() -> list:
    """Получает курсы валют (USD, EUR) к рублю через бесплатный API ЦБ РФ."""
    try:
        response = requests.get("https://cbr-xml-daily.ru", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [
                {"currency": "USD", "rate": round(data["Valute"]["USD"]["Value"], 2)},
                {"currency": "EUR", "rate": round(data["Valute"]["EUR"]["Value"], 2)},
            ]
    except requests.exceptions.RequestException:
        pass
    return [{"currency": "USD", "rate": 75.0}, {"currency": "EUR", "rate": 85.0}]


def get_stock_prices() -> list:
    """Возвращает базовые цены акций для S&P500."""
    stocks = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
    return [{"stock": stock, "price": 150.00} for stock in stocks]


def get_events_page(df: pd.DataFrame, date_str: str, range_type: str = "M") -> str:
    """Генерирует JSON-ответ для страницы 'События' по выбранному диапазону."""
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

    filtered_df = df[
        (df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)
    ].copy()

    expenses_df = filtered_df[filtered_df["Сумма операции"] < 0].copy()
    expenses_df["Сумма операции"] = expenses_df["Сумма операции"].abs()
    income_df = filtered_df[filtered_df["Сумма операции"] > 0]

    total_expenses = int(expenses_df["Сумма операции"].sum())
    cash_categories = ["Наличные", "Переводы"]

    transfers_df = expenses_df[expenses_df["Категория"].isin(cash_categories)]
    main_expenses_df = expenses_df[~expenses_df["Категория"].isin(cash_categories)]

    main_grouped = (
        main_expenses_df.groupby("Категория")["Сумма операции"].sum().reset_index()
    )
    main_grouped = main_grouped.sort_values(by="Сумма операции", ascending=False)

    if len(main_grouped) > 7:
        top_7 = main_grouped.head(7)
        others_sum = main_grouped.iloc[7:]["Сумма операции"].sum()
        others_df = pd.DataFrame(
            [{"Категория": "Остальное", "Сумма операции": others_sum}]
        )
        main_grouped = pd.concat([top_7, others_df], ignore_index=True)

    main_expenses_list = [
        {"category": row["Категория"], "amount": int(row["Сумма операции"])}
        for _, row in main_grouped.iterrows()
    ]

    transfers_grouped = (
        transfers_df.groupby("Категория")["Сумма операции"].sum().reset_index()
    )
    transfers_list = [
        {"category": row["Категория"], "amount": int(row["Сумма операции"])}
        for _, row in transfers_grouped.iterrows()
    ]

    total_income = int(income_df["Сумма операции"].sum())
    income_grouped = (
        income_df.groupby("Категория")["Сумма операции"].sum().reset_index()
    )
    income_list = [
        {"category": row["Категория"], "amount": int(row["Сумма операции"])}
        for _, row in income_grouped.iterrows()
    ]

    response_data = {
        "expenses": {
            "total_amount": total_expenses,
            "main": main_expenses_list,
            "transfers_and_cash": transfers_list,
        },
        "income": {"total_amount": total_income, "main": income_list},
        "currency_rates": get_currency_rates(),
        "stock_prices": get_stock_prices(),
    }

    return json.dumps(response_data, ensure_ascii=False, indent=2)
