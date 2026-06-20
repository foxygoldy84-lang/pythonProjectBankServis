import logging
import re
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger("services")


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """Сервис 'Инвесткопилка'.

    Корректно приводит любые форматы дат из Excel к YYYY-MM для точной фильтрации.
    """
    logger.info(f"Расчет инвесткопилки за месяц {month} с порогом {limit}")

    def match_month(item: Dict[str, Any]) -> bool:
        date_val = item.get("Дата операции") or item.get("Дата")
        if not date_val:
            return False
        try:
            # Надежно парсим дату через Pandas и приводим к единому формату YYYY-MM
            dt = pd.to_datetime(date_val, dayfirst=True)
            return dt.strftime("%Y-%m") == month and float(item.get("Сумма операции", 0)) < 0
        except (ValueError, TypeError):
            return False

    filtered_transactions = filter(match_month, transactions)

    total_saved = 0.0
    for t in filtered_transactions:
        amount = abs(float(t.get("Сумма операции", 0)))
        if amount % limit != 0:
            rounded_amount = ((amount // limit) + 1) * limit
            total_saved += rounded_amount - amount

    return round(total_saved, 2)


def process_bank_search(data: List[Dict[str, Any]], search: str) -> List[Dict[str, Any]]:
    """Простой поиск по подстроке.

    Возвращает список всех найденных транзакций для полного вывода по ТЗ.
    """
    logger.info(f"Запуск простого поиска по строке: '{search}'")
    filtered_data = []
    pattern = re.compile(search, re.IGNORECASE)

    for transaction in data:
        description = str(transaction.get("Описание", ""))
        category = str(transaction.get("Категория", ""))
        if pattern.search(description) or pattern.search(category):
            filtered_data.append(transaction)

    return filtered_data
