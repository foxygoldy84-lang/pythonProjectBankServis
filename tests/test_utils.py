import os
import json
from src.utils import load_user_settings


def test_load_user_settings_default():
    """Тест: если файла настроек нет, возвращаются дефолтные значения."""
    # Удаляем файл, если он вдруг есть (для чистоты теста)
    if os.path.exists("test_settings.json"):
        os.remove("test_settings.json")

    result = load_user_settings("test_settings.json")
    assert "user_currencies" in result
    assert "user_stocks" in result
    assert result["user_currencies"] == ["USD", "EUR"]


def test_load_user_settings_existing(tmp_path):
    """Тест: успешное чтение существующего файла настроек."""
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "custom_settings.json"

    custom_data = {"user_currencies": ["RUB"], "user_stocks": ["MSFT"]}
    p.write_text(json.dumps(custom_data))

    result = load_user_settings(str(p))
    assert result["user_currencies"] == ["RUB"]
    assert result["user_stocks"] == ["MSFT"]
