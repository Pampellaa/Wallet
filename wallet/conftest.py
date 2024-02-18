from datetime import date

import pytest
from django.contrib.auth.models import User

from wallet.models import Income, Category, Expense, Currency, Savings, Account, Transaction


@pytest.fixture
def user():
    return User.objects.create(username="test_user")


@pytest.fixture
def incomes(user, zloty):
    incomes = [
        Income.objects.create(amount=50, user=user, date='2024-08-01'),
        Income.objects.create(amount=100, user=user, date='2024-08-02'),
        Income.objects.create(amount=75, user=user, date='2024-08-03', category=Category.objects.create(name='wymiana'))
    ]
    return incomes


@pytest.fixture
def post_data(incomes):
    post_data = {
        'date_from': '2024-08-01',
        'date_to': '2024-08-02',
    }
    return post_data


@pytest.fixture
def expenses(user, zloty):
    expenses = [
        Expense.objects.create(amount=50, user=user, date='2024-08-01'),
        Expense.objects.create(amount=100, user=user, date='2024-08-02'),
        Expense.objects.create(amount=75, user=user, date='2024-08-03')
    ]
    return expenses


@pytest.fixture
def transaction_pln(user, zloty):
    return Transaction.objects.create(
        user=user,
        amount=30,
        date='2024-08-01',
        description='Test Description',
        category=None,
        transaction_type='Income',
        currency=zloty,
    )


@pytest.fixture
def transaction_for(user, foreign_currency):
    return Transaction.objects.create(
        user=user,
        amount=30,
        date='2024-08-01',
        description='Test Description',
        category=None,
        transaction_type='Income',
        currency=foreign_currency[0],
    )


@pytest.fixture
def post_data2(expenses):
    post_data2 = {
        'date_from': '2024-08-01',
        'date_to': '2024-08-02',
    }
    return post_data2


@pytest.fixture
def category(user):
    return Category.objects.create(name='Test Category', user=user)


@pytest.fixture
def main_category():
    return Category.objects.create(name='Main Category', is_built=True)


@pytest.fixture
def user_category(user):
    return Category.objects.create(name='User Category', is_built=False, user=user)


@pytest.fixture
def expense(user, user_category):
    return Expense.objects.create(
        user=user,
        category=user_category,
        amount=50,
        date=date.today(),
        description='Test Expense'
    )


@pytest.fixture
def income(user, user_category):
    return Income.objects.create(
        user=user,
        category=user_category,
        amount=100,
        date=date.today(),
        description='Test Income'
    )


@pytest.fixture
def zloty():
    currency = Currency.objects.create(id=153, name="Zloty", code='PLN', exchange_rate=1)
    return currency


@pytest.fixture
def saving(user):
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
    return savings


@pytest.fixture
def foreign_currency():
    currencies = [
        Currency.objects.create(code='AAA', name='AAA', exchange_rate=1),
        Currency.objects.create(code='BBB', name='BBB', exchange_rate=0.5),
        Currency.objects.create(code='CCC', name='CCC', exchange_rate=2)
    ]
    return currencies


@pytest.fixture
def foreign_accounts(user, foreign_currency):
    accounts = [
        Account.objects.create(name='AAA', balance='1', currency=foreign_currency[0], user=user),
        Account.objects.create(name='BBB', balance='2', currency=foreign_currency[1], user=user),
        Account.objects.create(name='CCC', balance='3', currency=foreign_currency[2], user=user),
    ]
    return accounts

@pytest.fixture
def account(user, foreign_currency):
    account = Account.objects.create(name='DDD', balance='100', currency=foreign_currency[0], user=user)
    return account


@pytest.fixture
def transactions(user, foreign_currency, category):
    transactions = [
        Transaction.objects.create(user=user,
                                   amount=100.50,
                                   date='2022-01-01',
                                   description='Test Description',
                                   category=category,
                                   transaction_type='Income',
                                   currency=foreign_currency[0])
    ]
    return transactions
