import json
from src.services import find_personal_transfers, find_phone_numbers


def test_find_phone_numbers():
    transactions = [{"id": 1, "Описание": "Оплата услуг МТС +7 921 11-22-33"}, {"id": 2, "Описание": "Без телефона"}]
    result = find_phone_numbers(transactions)
    assert len(json.loads(result)) == 1


def test_find_personal_transfers():
    transactions = [
        {"id": 1, "Описание": "Перевод Олегу Б.", "Категория": "Переводы"},
        {"id": 2, "Описание": "ООО Ромашка", "Категория": "Переводы"},
    ]
    result = find_personal_transfers(transactions)
    assert len(json.loads(result)) == 1
