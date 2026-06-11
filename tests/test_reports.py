import pandas as pd
from src.reports import spending_by_weekday


def test_spending_by_weekday_empty():
    """Тест: если датафрейм пустой, отчет возвращает пустую структуру с колонками."""
    empty_df = pd.DataFrame()
    result = spending_by_weekday(empty_df, date="20.05.2020")

    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ["День недели", "Средние траты"]
    assert len(result) == 0
