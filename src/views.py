import json
import requests
from datetime import datetime, timedelta
import pandas as pd
from typing import Union


def load_data(file_path):
    """Загрузка данных из Excel"""
    df = pd.read_excel(file_path)
    return df


def filter_data(df, start_date, end_date):
    # Преобразуем столбец дат в тип datetime
    df['Дата операции'] = pd.to_datetime(df['Дата операции'])

    # Преобразуем начальную и конечную даты в формат datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Проводим фильтрацию
    mask = (df['Дата операции'] >= start_date) & (df['Дата операции'] <= end_date)
    return df.loc[mask]

def calculate_total_spent(filtered_df: pd.DataFrame) -> dict:
    """
    Рассчитывает общую сумму расходов по каждой банковской карте.

    :param filtered_df: Отфильтрованный DataFrame с транзакционными данными.
    :return: Словарь, ключами которого являются номера карт (последние четыре цифры), значениями — общая сумма расходов.
    """
    total_spent = filtered_df.groupby('Номер карты')['Сумма платежа'].sum()
    return total_spent.to_dict()

def calculate_cashback(filtered_df: pd.DataFrame) -> dict:
    """
    Вычисляет общий кешбэк по каждой банковской карте (1% от потраченной суммы).

    :param filtered_df: Отфильтрованный DataFrame с транзакционными данными.
    :return: Словарь, содержащий номер карты (ключ) и соответствующий кешбэк (значение).
    """
    cashback_per_card = {}
    for card in filtered_df['Номер карты'].unique():
        df_card = filtered_df[filtered_df['Номер карты'] == card]
        spent_amount = df_card['Сумма платежа'].sum()
        cashback_amount = round(spent_amount / 100, 2)
        cashback_per_card[str(card)] = cashback_amount
    return cashback_per_card

def top_transactions(filtered_df: pd.DataFrame, n: int=5) -> list[dict]:
    """
    Возвращает список топ-N транзакций по размеру суммы платежа.

    :param filtered_df: Отфильтрованный DataFrame с транзакционными данными.
    :param n: Количество записей в списке (по умолчанию 5).
    :return: Список из N наиболее крупных транзакций с информацией о дате, сумме, категории и описании.
    """
    sorted_df = filtered_df.sort_values(by='Сумма платежа', ascending=False).head(n)
    result = []
    for _, row in sorted_df.iterrows():
        result.append({
            'date': row['Дата операции'],
            'amount': float(row['Сумма платежа']),
            'category': row['Категория'],
            'description': row['Описание']
        })
    return result

def fetch_currency_rates(user_currencies: list[str]) -> dict[str, float]:
    """
    Получает курсы валют по отношению к доллару USD.

    :param user_currencies: Список валют, для которых запрашиваются курсы.
    :type user_currencies: List[str]
    :return: Словарь, содержащий коды валют и соответствующие обменные курсы.
    :rtype: Dict[str, float]
    """
    api_key = 'YOUR_API_KEY'
    base_url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency={user_currencies}&apikey={api_key}'
    response = requests.get(base_url)
    data = response.json()
    rates = {item['Currency Code']: float(item['Exchange Rate']) for item in data['Realtime Currency Exchange Rates']}
    return rates


def fetch_stock_prices(user_stocks: list[str]) -> list[dict[str, Union[str, float]]]:
    """
    Запрашивает текущие цены акций из списка выбранных тикеров.

    :param user_stocks: Список тикеров акций, для которых запрашиваются текущие котировки.
    :type user_stocks: List[str]
    :return: Список объектов, содержащих тикеры акций и их текущие цены.
    :rtype: List[Dict[str, Union[str, float]]]
    """
    api_key = 'YOUR_API_KEY'
    stock_prices = []
    for stock in user_stocks:
        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={api_key}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get("Global Quote")
            if data is not None:
                price = float(data['05. price'])
                stock_prices.append({'stock': stock, 'price': price})
    return stock_prices

def greeting_message(current_time: pd.DataFrame) -> str:
    """
    Определяет подходящее приветственное сообщение в зависимости от текущего часа.

    :param current_time: Объект datetime с текущей временной меткой.
    :type current_time: datetime.datetime
    :return: Строка с соответствующим приветствием ("Доброе утро", "Добрый день", "Добрый вечер", "Доброй ночи").
    :rtype: str
    """
    hour = current_time.hour
    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 24:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def main(date_str: str) -> dict:
    """
       Основная функция для генерации отчета о расходах и состоянии финансов.

       Эта функция принимает строку с датой и временем в формате YYYY-MM-DD HH:MM:SS, обрабатывает входящие данные и формирует полный отчёт.

       Параметры:
       ----------
       date_str : str
           Дата и время в формате строки "%Y-%m-%d %H:%M:%S", используемые для расчёта периода отчетности.

       Возвращаемое значение:
       ----------------------
       dict
           JSON-подобный словарь с полными результатами отчёта, включающими приветствие, статистику по картам,
           топ-платежи, курсы валют и стоимость акций.

       Примечания:
       ---------
       Используется библиотека Pandas для обработки данных и запросов HTTP для получения текущих значений валют и акций.
       Данные загружаются из Excel-файла, настройки берутся из файла user_settings.json.
       """

    date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    month_start = date_obj.replace(day=1, hour=0, minute=0, second=0)
    file_path = 'operations.xls'
    df = load_data(file_path)
    filtered_df = filter_data(df, month_start, date_obj)

    cards_summary = calculate_total_spent(filtered_df)
    cashbacks = calculate_cashback(filtered_df)
    top_trans = top_transactions(filtered_df)

    with open('user_settings.json', 'r') as settings_file:
        user_settings = json.load(settings_file)

    currency_rates = fetch_currency_rates(user_settings["user_currencies"])
    stock_prices = fetch_stock_prices(user_settings["user_stocks"])

    greeting = greeting_message(date_obj)

    output_json = {
        "greeting": greeting,
        "cards": [{
            "last_digits": str(card),
            "total_spent": float(cards_summary.get(str(card))),
            "cashback": float(cashbacks.get(str(card)))
        } for card in cards_summary.keys()],
        "top_transactions": top_trans,
        "currency_rates": list(currency_rates.items()),
        "stock_prices": stock_prices
    }

    return output_json