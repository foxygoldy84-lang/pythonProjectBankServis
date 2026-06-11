import logging
import re
from typing import Any, Dict, List

# Настраиваем логер для модуля сервисов
logger = logging.getLogger("services")


def investment_bank(
    month: str, transactions: List[Dict[str, Any]], limit: int
) -> float:
    """
    Сервис 'Инвесткопилка'.
    Использует элементы функционального программирования (filter, lambda).
    Округляет траты до заданного порога и считает накопления.
    """
    logger.info(
        f"Расчет инвесткопилки за месяц {month} с порогом округления {limit} руб."
    )

    # Фильтруем транзакции: оставляем только нужный месяц и только расходы (сумма < 0)
    filtered_transactions = filter(
        lambda t: str(t.get("Дата операции")).startswith(month)
        and float(t.get("Сумма операции", 0)) < 0,
        transactions,
    )

    total_saved = 0.0

    for t in filtered_transactions:
        amount = abs(float(t["Сумма операции"]))
        # Если сумма не делится на лимит ровно, вычисляем хвостик для копилки
        if amount % limit != 0:
            rounded_amount = ((amount // limit) + 1) * limit
            total_saved += rounded_amount - amount

    logger.info(
        f"Расчет копилки завершен. Успешно отложено: {round(total_saved, 2)} руб."
    )
    return round(total_saved, 2)


def process_bank_search(
    data: List[Dict[str, Any]], search: str
) -> List[Dict[str, Any]]:
    """
    Твоя функция 'Простой поиск' из прошлого проекта.
    Регистронезависимо ищет совпадения по строке в описании или категории.
    """
    logger.info(f"Запуск простого поиска по строке: '{search}'")
    filtered_data = []
    pattern = re.compile(search, re.IGNORECASE)

    for transaction in data:
        description = str(transaction.get("Описание", ""))
        category = str(transaction.get("Категория", ""))

        # Расширенный поиск: проверяем совпадение и в описании, и в категории
        if pattern.search(description) or pattern.search(category):
            filtered_data.append(transaction)

    logger.info(f"Поиск завершен. Найдено совпадений: {len(filtered_data)}")
    return filtered_data
