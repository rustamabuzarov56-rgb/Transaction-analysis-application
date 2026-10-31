import pandas as pd
import requests


def load_data(file_path: str) -> pd.DataFrame:
    """Загрузка данных из Excel"""
    df = pd.read_excel(file_path)
    return df


def filter_data(df: pd.DataFrame, start_date: str | pd.Timestamp, end_date: str | pd.Timestamp) -> pd.DataFrame:
    # Преобразуем столбец дат в тип datetime
    df["Дата операции"] = pd.to_datetime(df["Дата операции"])

    # Преобразуем начальную и конечную даты в формат datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Проводим фильтрацию
    mask = (df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)
    return df.loc[mask]


def calculate_total_spent(filtered_df: pd.DataFrame) -> dict:
    """
    Рассчитывает общую сумму расходов по каждой банковской карте.
    """
    total_spent = filtered_df.groupby("Номер карты")["Сумма платежа"].sum()
    return total_spent.to_dict()


def calculate_cashback(filtered_df: pd.DataFrame) -> dict:
    """
    Вычисляет общий кешбэк по каждой банковской карте (1% от потраченной суммы).
    """
    cashback_per_card = {}
    for card in filtered_df["Номер карты"].unique():
        df_card = filtered_df[filtered_df["Номер карты"] == card]
        spent_amount = df_card["Сумма платежа"].sum()
        cashback_amount = round(spent_amount / 100, 2)
        cashback_per_card[str(card)] = cashback_amount
    return cashback_per_card


def top_transactions(filtered_df: pd.DataFrame, n: int = 5) -> list[dict]:
    """
    Возвращает список топ-N транзакций по размеру суммы платежа.
    """
    sorted_df = filtered_df.sort_values(by="Сумма платежа", ascending=False).head(n)
    result = []
    for _, row in sorted_df.iterrows():
        result.append(
            {
                "date": row["Дата операции"],
                "amount": float(row["Сумма платежа"]),
                "category": row["Категория"],
                "description": row["Описание"],
            }
        )
    return result


def fetch_currency_rates(user_currencies: list[str]) -> dict[str, float]:
    """
    Получает курсы валют по отношению к доллару USD.
    """
    api_key = "YOUR_API_KEY"
    base_url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency={user_currencies}&apikey={api_key}"
    response = requests.get(base_url)
    data = response.json()
    rates = {item["Currency Code"]: float(item["Exchange Rate"]) for item in data["Realtime Currency Exchange Rates"]}
    return rates


def fetch_stock_prices(user_stocks: list[str]) -> list[dict[str, str | float]]:
    """
    Запрашивает текущие цены акций из списка выбранных тикеров.
    """
    api_key = "YOUR_API_KEY"
    stock_prices = []
    for stock in user_stocks:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get("Global Quote")
            if data is not None:
                price = float(data["05. price"])
                stock_prices.append({"stock": stock, "price": price})
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
