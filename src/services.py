import re
import json
import logging
from typing import Any

def find_phon_numbers(transactions: list[dict[str, Any]]) -> str:
    """Функция возвращает JSON со всеми транзакциями, содержащими в описании российские мобильные номера."""
    phon_pattern = r'\+7\s\d{3}\s\d{2}-\d{2}-\d{2}'
    results = []
    try:
        for transaction in transactions:
            description = transaction.get('Описание', '')
            match = re.search(phon_pattern, description)
            if match:
                results.append(transaction)
    except Exception as e:
        logging.error(f"Ошибка при поиске телефонных номеров: {e}")
    return json.dumps(results, ensure_ascii=False, indent=4)

def find_phone_numbers(transactions: list[dict[str, Any]]) -> str:
    """Функция возвращает JSON со всеми транзакциями, содержащими в описании российские мобильные номера."""
    phone_pattern = r'\+7\s\d{3}\s\d{2}-\d{2}-\d{2}'
    results = []

    try:
        for transaction in transactions:
            description = transaction.get('Описание', '')
            match = re.search(phone_pattern, description)
            if match:
                results.append(transaction)
    except Exception as e:
        logging.error(f"Ошибка при поиске телефонных номеров: {e}")

    return json.dumps(results, ensure_ascii=False, indent=4)

