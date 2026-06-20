import json
import logging
import os
from typing import Any, Dict, List

import pandas as pd

# Создаем папку для логов, как в моем прошлом проекте
os.makedirs("logs", exist_ok=True)

# Настройка логера в моем стиле
logger = logging.getLogger("utils")
file_handler = logging.FileHandler("logs/utils.log", mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


def read_transactions_dataframe(file_path: str) -> pd.DataFrame:
    """Считывает транзакции в виде DataFrame для модулей веб-страниц и отчетов."""
    logger.info(f"Запрос на чтение DataFrame из Excel-файла: {file_path}")
    if not os.path.exists(file_path):
        logger.warning(f"Файл не найден по пути: {file_path}")
        return pd.DataFrame()
    try:
        df = pd.read_excel(file_path)
        logger.info(f"Успешно загружено {len(df)} строк для анализа DataFrame")
        return df
    except Exception as e:
        logger.error(f"Ошибка чтения Excel-файла в DataFrame {file_path}: {e}")
        return pd.DataFrame()


def read_transactions_xlsx(file_path: str) -> List[Dict[str, Any]]:
    """
    Моя прошлая функция: считывает операции из Excel и приводит к виду списка словарей.
    Адаптирована под новые названия колонок для Инвесткопилки.
    """
    logger.info(f"Запрос на чтение списка словарей для сервисов из Excel: {file_path}")

    if not os.path.exists(file_path):
        logger.warning(f"Excel-файл не найден по пути: {file_path}")
        return []

    try:
        df = pd.read_excel(file_path)
        # Заменяем пустые значения (NaN) на None, как в моем коде
        df = df.astype(object).where(pd.notnull(df), None)

        transactions = []
        for _, row in df.iterrows():
            # Сохраняем структуру, адаптируя под поля нового задания
            transaction = {
                "Дата операции": row.get("Дата операции") or row.get("Дата"),
                "Сумма операции": row.get("Сумма операции") or row.get("Сумма"),
                "Категория": row.get("Категория"),
                "Описание": row.get("Описание") or row.get("description"),
            }
            transactions.append(transaction)

        logger.info(f"Excel успешно обработан для сервисов. Найдено транзакций: {len(transactions)}")
        return transactions
    except OSError as e:
        logger.error(f"Ошибка ввода-вывода при чтении Excel-файла {file_path}: {e}")
        return []


def load_user_settings(
    settings_path: str = "user_settings.json",
) -> Dict[str, List[str]]:
    """Загружает настройки валют и акций из JSON."""
    if not os.path.exists(settings_path):
        return {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN"]}
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN"]}
