import functools
import logging
from datetime import datetime
from typing import Any, Callable, Optional

import pandas as pd

# Настраиваем логирование для отчетов
logger = logging.getLogger("reports")


def save_report_to_file(filename: Optional[str] = None) -> Callable:
    """
    Мой доработанный декоратор из прошлого проекта.
    Записывает в файл результат (DataFrame), который возвращает функция отчета.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                # Запускаем функцию отчета и получаем результат (DataFrame)
                result = func(*args, **kwargs)

                # Определяем имя файла: переданное или по умолчанию
                actual_filename = filename or f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

                # Записываем результат в файл
                if isinstance(result, pd.DataFrame):
                    if actual_filename.endswith(".xlsx"):
                        result.to_excel(actual_filename, index=False)
                    else:
                        result.to_csv(actual_filename, index=False, encoding="utf-8")
                    logger.info(f"Отчет {func.__name__} успешно сохранен в {actual_filename}")

                return result

            except Exception as e:
                # Логируем ошибку, если что-то пошло не так, как в моем старом декораторе
                log_message = f"{func.__name__} error: {type(e).__name__}. Inputs: {args}, {kwargs}"
                logger.error(log_message)
                raise e

        return wrapper

    return decorator


@save_report_to_file(filename="spending_by_weekday.csv")
def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """
    Принимает DataFrame с транзакциями и возвращает средние траты
    в каждый из дней недели за последние три месяца от переданной даты.
    """
    if transactions.empty:
        return pd.DataFrame(columns=["День недели", "Средние траты"])

    # Определяем целевую дату (если не передана, берем текущую)
    if date:
        try:
            target_date = pd.to_datetime(date, dayfirst=True)
        except (ValueError, TypeError):
            target_date = pd.to_datetime(date)
    else:
        target_date = pd.Timestamp(datetime.now())

    # Приводим даты к формату datetime для фильтрации
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)
    start_date = target_date - pd.Timedelta(days=90)

    # Фильтруем только расходы за последние 3 месяца
    filtered_df = transactions[
        (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= target_date)
        & (transactions["Сумма операции"] < 0)
    ].copy()

    if filtered_df.empty:
        return pd.DataFrame(columns=["День недели", "Средние траты"])

    # Делаем траты положительными числами
    filtered_df["Сумма операции"] = filtered_df["Сумма операции"].abs()

    # Маппинг дней недели на русский язык
    weekdays_map = {
        "Monday": "Понедельник",
        "Tuesday": "Вторник",
        "Wednesday": "Среда",
        "Thursday": "Четверг",
        "Friday": "Пятница",
        "Saturday": "Суббота",
        "Sunday": "Воскресенье",
    }
    filtered_df["День недели"] = filtered_df["Дата операции"].dt.day_name().map(weekdays_map)

    # Считаем средние траты и округляем их
    result = filtered_df.groupby("День недели", observed=False)["Сумма операции"].mean().reset_index()
    result.columns = ["День недели", "Средние траты"]
    result["Средние траты"] = result["Средние траты"].round().astype(int)

    # Сортируем дни по порядку от понедельника до воскресенья
    days_order = [
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
        "Воскресенье",
    ]
    result["День недели"] = pd.Categorical(result["День недели"], categories=days_order, ordered=True)

    return result.sort_values("День недели")
