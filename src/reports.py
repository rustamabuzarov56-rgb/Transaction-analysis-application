import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
import json
import logging
from functools import wraps

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def report_to_file(filename=None):
    """
    Декорирует функцию таким образом, что её результат сохраняется в JSON-файл.

    Если filename передан, сохраняет в указанный файл,
    иначе создает файл 'report_default.json'.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Имя файла по умолчанию
            file_name = filename or f'report_{func.__name__}.json'

            with open(file_name, 'w') as f:
                json.dump(result.to_dict(), f, indent=4)

            logger.info(f'Отчёт сохранён в {file_name}')
            return result

        return wrapper

    return decorator


@report_to_file()
def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """
    Вычисляет средние ежедневные расходы за последние три месяца (рабочие дни vs выходные),
    начиная с указанной даты (или текущей даты, если аргумент не указан).
    """
    if not isinstance(transactions, pd.DataFrame):
        raise TypeError("Переданный объект не является Pandas DataFrame.")

    if len(transactions) == 0:
        raise ValueError("Нет данных для обработки.")

    # Конвертируем строку даты в нужный формат (если указана)
    try:
        start_date = datetime.strptime(date, '%Y-%m-%d').date() if date else datetime.now().date()
    except Exception as e:
        raise ValueError(f"Ошибка преобразования даты: {e}")

    # Рассчитываем начало периода трех месяцев назад
    three_months_ago = start_date - timedelta(days=90)

    # Фильтруем транзакции за период
    filtered_transactions = transactions[
        (transactions['transaction_date'] >= three_months_ago.strftime('%Y-%m-%d')) &
        (transactions['transaction_date'] <= start_date.strftime('%Y-%m-%d'))
        ]

    # Определяем типы дней (рабочие / выходные)
    filtered_transactions['is_weekend'] = (
        filtered_transactions['transaction_date'].dt.dayofweek.isin([5, 6])
    )

    # Группируем и вычисляем среднее значение
    avg_spending = filtered_transactions.groupby('is_weekend')['amount'].mean()

    # Формирование итогового фрейма
    result_df = pd.DataFrame({
        'Day Type': ['Weekdays', 'Weekends'],
        'Average Spending': [
            round(avg_spending.get(False, 0), 2),
            round(avg_spending.get(True, 0), 2)
        ]
    })

    return result_df.set_index('Day Type')

data = {
    'transaction_date': ['2023-08-01', '2023-08-02', '2023-08-03',
                         '2023-08-04', '2023-08-05', '2023-08-06'],
    'amount': [100, 150, 200, 120, 180, 250]
}
df = pd.DataFrame(data)
df['transaction_date'] = pd.to_datetime(df['transaction_date'])
result = spending_by_workday(df, '2023-08-06')
print(result)
