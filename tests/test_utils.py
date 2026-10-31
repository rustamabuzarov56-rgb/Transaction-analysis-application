import pandas as pd
import requests_mock
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.utils import (load_data, filter_data, calculate_total_spent, calculate_cashback, top_transactions,
                       fetch_currency_rates, fetch_stock_prices, greeting_message)

class TestLoadData(unittest.TestCase):
    @patch('pandas.read_excel')
    def test_load_data(self, mock_read_excel):
        mock_read_excel.return_value = pd.DataFrame({'Column1': [1, 2], 'Column2': [3, 4]})
        df = load_data('sample_data.xlsx')
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(list(df.columns), ['Column1', 'Column2'])


class TestFilterData(unittest.TestCase):
    def test_filter_data(self):
        df = pd.DataFrame({
            'Дата операции': ['2023-01-01', '2023-01-15', '2023-02-01'],
            'Сумма платежа': [100, 200, 300],
            'Номер карты': ['card1', 'card2', 'card3']
        })
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 31)
        result = filter_data(df, start_date, end_date)

        # Конвертируем даты в string для простого сравнения
        dates_in_result = result['Дата операции'].dt.strftime('%Y-%m-%d').values

        self.assertIn('2023-01-01', dates_in_result)
        self.assertIn('2023-01-15', dates_in_result)
        self.assertNotIn('2023-02-01', dates_in_result)
class TestCalculateTotalSpent(unittest.TestCase):
    def test_calculate_total_spent(self):
        df = pd.DataFrame({
            'Номер карты': ['card1', 'card1', 'card2'],
            'Сумма платежа': [100, 200, 300]
        })
        result = calculate_total_spent(df)
        self.assertAlmostEqual(result['card1'], 300)
        self.assertAlmostEqual(result['card2'], 300)

class TestCalculateCashback(unittest.TestCase):
    def test_calculate_cashback(self):
        df = pd.DataFrame({
            'Номер карты': ['card1', 'card1', 'card2'],
            'Сумма платежа': [100, 200, 300]
        })
        result = calculate_cashback(df)
        self.assertAlmostEqual(result['card1'], 3.0)
        self.assertAlmostEqual(result['card2'], 3.0)

class TestTopTransactions(unittest.TestCase):
    def test_top_transactions(self):
        df = pd.DataFrame({
            'Дата операции': ['2023-01-01', '2023-01-15', '2023-02-01'],
            'Сумма платежа': [100, 200, 300],
            'Категория': ['Food', 'Transport', 'Shopping'],
            'Описание': ['Pizza', 'Bus ticket', 'New clothes']
        })
        result = top_transactions(df, n=2)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['amount'], 300)
        self.assertEqual(result[1]['amount'], 200)

class TestFetchCurrencyRates(unittest.TestCase):
    @requests_mock.Mocker()
    def test_fetch_currency_rates(self, m):
        m.get('https://www.alphavantage.co/query?',
              json={"Realtime Currency Exchange Rates":
                   [{"Currency Code": "EUR", "Exchange Rate": "0.9"},
                    {"Currency Code": "GBP", "Exchange Rate": "0.8"}]}
             )
        result = fetch_currency_rates(["EUR", "GBP"])
        self.assertEqual(result["EUR"], 0.9)
        self.assertEqual(result["GBP"], 0.8)

class TestFetchStockPrices(unittest.TestCase):
    @requests_mock.Mocker()
    def test_fetch_stock_prices(self, m):
        m.get('https://www.alphavantage.co/query?',
              json={'Global Quote':
                   {'05. price': '1000'}})
        result = fetch_stock_prices(["TSLA"])
        self.assertEqual(result[0]["stock"], "TSLA")
        self.assertEqual(result[0]["price"], 1000.0)

class TestGreetingMessage(unittest.TestCase):
    def test_greeting_message(self):
        now = datetime.now()
        morning = datetime(now.year, now.month, now.day, 8, 0, 0)
        afternoon = datetime(now.year, now.month, now.day, 14, 0, 0)
        evening = datetime(now.year, now.month, now.day, 20, 0, 0)
        night = datetime(now.year, now.month, now.day, 2, 0, 0)

        self.assertEqual(greeting_message(morning), "Доброе утро")
        self.assertEqual(greeting_message(afternoon), "Добрый день")
        self.assertEqual(greeting_message(evening), "Добрый вечер")
        self.assertEqual(greeting_message(night), "Доброй ночи")
