import json
from datetime import datetime

from src.utils import (load_data, filter_data, calculate_total_spent, calculate_cashback,
                       top_transactions, fetch_currency_rates, fetch_stock_prices, greeting_message)


def main(date_str: str) -> dict:
    """
    Эта функция принимает строку с датой и временем в формате YYYY-MM-DD HH:MM:SS, обрабатывает входящие данные
     и формирует полный отчёт.
    """

    date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    month_start = date_obj.replace(day=1, hour=0, minute=0, second=0)
    file_path = "operations.xls"
    df = load_data(file_path)
    filtered_df = filter_data(df, month_start, date_obj)

    cards_summary = calculate_total_spent(filtered_df)
    cashbacks = calculate_cashback(filtered_df)
    top_trans = top_transactions(filtered_df)

    with open("user_settings.json", "r") as settings_file:
        user_settings = json.load(settings_file)

    currency_rates = fetch_currency_rates(user_settings["user_currencies"])
    stock_prices = fetch_stock_prices(user_settings["user_stocks"])

    greeting = greeting_message(date_obj)

    output_json = {
        "greeting": greeting,
        "cards": [
            {
                "last_digits": str(card),
                "total_spent": float(cards_summary.get(str(card))),
                "cashback": float(cashbacks.get(str(card))),
            }
            for card in cards_summary.keys()
        ],
        "top_transactions": top_trans,
        "currency_rates": list(currency_rates.items()),
        "stock_prices": stock_prices,
    }

    return output_json
