from datetime import datetime

import pandas as pd
import pytest

from src.reports import spending_by_workday


@pytest.fixture(scope="module")
def simple_dataframe():
    data = {
        "transaction_date": ["2023-08-01", "2023-08-02", "2023-08-03", "2023-08-04", "2023-08-05", "2023-08-06"],
        "amount": [100, 150, 200, 120, 180, 250],
    }
    df = pd.DataFrame(data)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    return df


@pytest.fixture(scope="module")
def empty_dataframe():
    return pd.DataFrame(columns=["transaction_date", "amount"])


def test_empty_dataframe(empty_dataframe):
    """Проверяем поведение при передаче пустого датафрейма."""
    with pytest.raises(ValueError, match="Нет данных"):
        spending_by_workday(empty_dataframe)


def test_invalid_type():
    """Тестируем исключение при передаче неверного типа данных."""
    invalid_input = {"transaction_date": [], "amount": []}
    with pytest.raises(TypeError, match="не является Pandas DataFrame"):
        spending_by_workday(invalid_input)


def test_valid_data(simple_dataframe):
    """Простое тестирование валидных данных."""
    expected_output = pd.DataFrame(
        index=["Weekdays", "Weekends"],
        columns=["Average Spending"],
        data={"Average Spending": [142.5, 215.0]},
    ).round(2)
    result = spending_by_workday(simple_dataframe, "2023-08-06")
    assert result.equals(expected_output)


def test_current_date(simple_dataframe):
    """Проверка на работу с текущей датой."""
    today = datetime.today().strftime("%Y-%m-%d")
    result = spending_by_workday(simple_dataframe)
    assert isinstance(result, pd.DataFrame)


def test_bad_date_format(simple_dataframe):
    """Обработка ошибочного формата даты."""
    with pytest.raises(ValueError, match="Ошибка преобразования даты"):
        spending_by_workday(simple_dataframe, "invalid-date-format")


def test_report_saved(tmp_path):
    """Проверка наличия файла с результатом."""
    from src.reports import report_to_file

    test_filename = tmp_path / "test_report.json"

    # Создаем минималистичный датафрейм
    test_data = pd.DataFrame({"column1": ["value"]})

    @report_to_file(test_filename)
    def dummy_function():
        return test_data  # Здесь возвращаем датафрейм

    dummy_function()
    assert test_filename.exists()
