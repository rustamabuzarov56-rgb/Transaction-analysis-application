import pandas as pd
import datetime
import json
from unittest.mock import patch, MagicMock
from src.views import (load_data,filter_data, calculate_total_spent, calculate_cashback, top_transactions, greeting_message, main)


# Фиктивная функция загрузки данных
def load_data(file_path):
    data = {
        'Номер карты': ['1234', '5678'],
        'Сумма платежа': [100, 200],
        'Дата операции': ['2023-01-01', '2023-01-02']
    }
    df = pd.DataFrame(data)
    return df

# Тест для функции загрузки данных
def test_load_data():
    df = load_data('dummy')
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0

# Тест для функции расчета общих затрат
def test_calculate_total_spent():
    data = {
        'Номер карты': ['1234', '1234', '5678'],
        'Сумма платежа': [100, 200, 300]
    }
    df = pd.DataFrame(data)
    result = calculate_total_spent(df)
    expected_result = {'1234': 300.0, '5678': 300.0}
    assert result == expected_result

# Тест для функции расчета кешбэка
def test_calculate_cashback():
    data = {
        'Номер карты': ['1234', '1234', '5678'],
        'Сумма платежа': [100, 200, 300]
    }
    df = pd.DataFrame(data)
    result = calculate_cashback(df)
    expected_result = {'1234': 3.0, '5678': 3.0}
    assert result == expected_result

# Тест для приведения сообщения-приветствия
def test_greeting_message():
    time_early = datetime.datetime(2023, 1, 1, 7, 0, 0)
    time_late = datetime.datetime(2023, 1, 1, 23, 0, 0)
    morning_msg = greeting_message(time_early)
    evening_msg = greeting_message(time_late)
    assert morning_msg == "Доброе утро"
    assert evening_msg == "Добрый вечер"