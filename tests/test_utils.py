import pytest
from src.views import get_date_range

@pytest.mark.parametrize(
    ('input_date', 'expected_period'), [
        ('2020-05-20', ('2020-05-01', '2020-05-31')),
        ('2020-01-15', ('2020-01-01', '2020-01-31')),
    ]
)
def test_get_date_range(input_date, expected_period):
    actual_period = get_date_range(input_date)
    assert actual_period == expected_period