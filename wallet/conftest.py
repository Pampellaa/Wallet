import pytest
from django.contrib.auth.models import User

from wallet.models import Income, Category, Expense, Currency, Savings


@pytest.fixture
def income():
    user = User.objects.create(username="test_user")
    incomes =[
        Income.objects.create(amount=50, user=user, date='2024-08-01'),
        Income.objects.create(amount=100, user=user, date='2024-08-02'),
        Income.objects.create(amount=75, user=user, date='2024-08-03')
    ]
    return user, incomes
@pytest.fixture
def income2(income):
    post_data = {
        'date_from': '2024-08-01',
        'date_to': '2024-08-02',
    }
    return income, post_data

@pytest.fixture
def expense():
    user = User.objects.create(username="test_user")
    expenses = [
        Expense.objects.create(amount=50, user=user, date='2024-08-01'),
        Expense.objects.create(amount=100, user=user, date='2024-08-02'),
        Expense.objects.create(amount=75, user=user, date='2024-08-03')
    ]
    return user, expenses
@pytest.fixture
def expense2(expense):
    post_data = {
        'date_from': '2024-08-01',
        'date_to': '2024-08-02',
    }
    return expense, post_data

@pytest.fixture
def zloty():
    currency = Currency.objects.create(id=153, name="Zloty", code='PLN', exchange_rate=1)
    return currency

@pytest.fixture
def saving():
    user = User.objects.create(username="test_user")
    savings = [
        Savings.objects.create(
            user=user,
            name='Test Savings',
            start_date='2022-01-01',
            end_date='2022-12-31',
            goal_amount=1000.00,
            current_amount=500.00,
            remaining_amount=500.00,
            last_deposit_date='2022-01-15'
        ),
        Savings.objects.create(
            user=user,
            name='Test Savings2',
            start_date='2022-01-01',
            end_date='2022-12-11',
            goal_amount=100.00,
            current_amount=50.00,
            remaining_amount=50.00,
            last_deposit_date='2022-01-15'
        )
    ]
    return user, savings