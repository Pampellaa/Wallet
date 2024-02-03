from datetime import datetime
from decimal import Decimal

import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User, AnonymousUser
from pytest_django.asserts import assertRedirects

from wallet.forms import IncomeAddForm, ExpenseAddForm, SavingsAddForm, LoginForm, RegisterForm, CategoryAddForm, \
    AccountAddForm, ForIncomeAddForm, ForExpenseAddForm
from wallet.models import Income, Category, Transaction, Expense, Savings, Account
from wallet.views import CategoryView


@pytest.mark.django_db
def test_dashboard(user, expenses, incomes, transaction_pln, transaction_for, foreign_accounts):
    client = Client()
    client.force_login(user)
    url = reverse('dashboard')
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['sum_expenses'] == Decimal('225.0')
    assert response.context['sum_income'] == Decimal('225.0')
    assert response.context['together'] == Decimal('0')
    assert response.context['sum_expenses_round'] == 225
    assert response.context['sum_income_round'] == 225
    assert response.context['transactionsPLN'].count() == 1
    assert response.context['transactionsFOR'].count() == 1
    assert response.context['account'].count() == 3


@pytest.mark.django_db
def test_dashboard_nolog():
    client = Client()
    url = reverse('dashboard')
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('login') in response.url


@pytest.mark.django_db
def test_login_get():
    client = Client()
    url = reverse('login')
    response = client.get(url)
    assert response.status_code == 200
    assert isinstance(response.context['form'], LoginForm)


@pytest.mark.django_db
def test_login_post_valid():
    client = Client()
    url = reverse('login')
    user = User.objects.create_user(username='test', password='testpassword')
    data = {'username': 'test', 'password': 'testpassword'}
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('dashboard')


@pytest.mark.django_db
def test_login_post_invalid():
    client = Client()
    url = reverse('login')
    data = {'username': 'testinvalid', 'password': 'testpassword'}
    response = client.post(url, data)
    assert response.status_code == 200
    assert list(response.context['messages'])[0].message == 'Nieprawidłowe dane logowania. Spróbuj ponownie.'


@pytest.mark.django_db
def test_logout():
    client = Client()
    user = User.objects.create_user(username='test')
    client.force_login(user)
    url = reverse('logout')
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('index')
    assert isinstance(response.wsgi_request.user, AnonymousUser)


@pytest.mark.django_db
def test_register_get():
    client = Client()
    url = reverse('register')
    response = client.get(url)
    assert response.status_code == 200
    assert isinstance(response.context['form'], RegisterForm)


@pytest.mark.django_db
def test_register_valid_post():
    client = Client()
    url = reverse('register')
    data = {'username': 'test',
            'password1': 'testpassword',
            'password2': 'testpassword'}
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('login')


@pytest.mark.django_db
def test_register_invalid_password_no_match_post():
    client = Client()
    url = reverse('register')
    data = {'username': 'test',
            'password1': 'testpassword',
            'password2': 'invalidpassword'}
    response = client.post(url, data)
    assert response.status_code == 200
    assert 'password2' in response.context['form'].errors
    assert 'Hasła nie pasują do siebie.' in response.context['form'].errors['password2']


@pytest.mark.django_db
def test_register_invalid_username_exists():
    user = User.objects.create_user(username='test')
    client = Client()
    url = reverse('register')
    data = {'username': 'test',
            'password1': 'testpassword',
            'password2': 'testpassword'}
    response = client.post(url, data)
    assert response.status_code == 200
    assert 'username' in response.context['form'].errors


@pytest.mark.django_db
def test_income_get(incomes, user):
    client = Client()
    client.force_login(user)
    url = reverse('income')
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['incomes'].count() == 3
    expected_total_income = sum(income.amount for income in incomes)
    assert response.context['total_income'] == expected_total_income


@pytest.mark.django_db
def test_income_post(incomes, post_data, user):
    client = Client()
    client.force_login(user)
    url = reverse('income')
    response = client.post(url, data=post_data)
    assert response.status_code == 200
    assert response.context['incomes'].count() == 2
    expected_total_income = 50 + 100
    assert response.context['total_income'] == expected_total_income


@pytest.mark.django_db
def test_income_nolog():
    client = Client()
    url = reverse('income')
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('login') in response.url


@pytest.mark.django_db
def test_expense_get(expenses, user):
    client = Client()
    client.force_login(user)
    url = reverse('expense')
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['expenses'].count() == 3
    expected_total_expense = sum(expense.amount for expense in expenses)
    assert response.context['total_expense'] == expected_total_expense


@pytest.mark.django_db
def test_expense_post(expense, post_data2, user):
    client = Client()
    client.force_login(user)
    url = reverse('expense')
    response = client.post(url, data=post_data2)
    assert response.status_code == 200
    assert response.context['expenses'].count() == 2
    expected_total_expense = 50 + 100
    assert response.context['total_expense'] == expected_total_expense


@pytest.mark.django_db
def test_expense_nolog():
    client = Client()
    url = reverse('expense')
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('login') in response.url


@pytest.mark.django_db
def test_incomeAdd_get(category, user):
    client = Client()
    client.force_login(user)
    url = reverse('income_add')
    response = client.get(url)
    assert response.status_code == 200
    assert isinstance(response.context['form'], IncomeAddForm)


@pytest.mark.django_db
def test_incomeAdd_post(user, category, zloty):
    client = Client()
    client.force_login(user)
    url = reverse('income_add')
    data = {
        'amount': 100,
        'date': '2020-05-21',
        'description': 'test description',
        'category': category.id,
        'user': user.id
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('income')
    assert Income.objects.get(amount=data['amount'],
                              date=data['date'],
                              description=data['description'],
                              category=category,
                              user=user)
    assert Transaction.objects.get(amount=data['amount'],
                                   date=data['date'],
                                   description=data['description'],
                                   category=category,
                                   user=user,
                                   transaction_type='Income')


@pytest.mark.django_db
def test_income_add_nolog():
    client = Client()
    url = reverse('income_add')
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('login') in response.url


@pytest.mark.django_db
def test_expense_add_get(user):
    client = Client()
    client.force_login(user)
    url = reverse('expense_add')
    response = client.get(url)
    assert response.status_code == 200
    assert isinstance(response.context['form'], ExpenseAddForm)


@pytest.mark.django_db
def test_expense_add_post(user, category, zloty):
    client = Client()
    client.force_login(user)
    url = reverse('expense_add')
    data = {
        'amount': 100,
        'date': '2020-05-21',
        'description': 'test description',
        'category': category.id,
        'user': user.id
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('expense')
    assert Expense.objects.get(
        amount=data['amount'],
        date=data['date'],
        description=data['description'],
        category=category,
        user=user
    )
    assert Transaction.objects.get(
        amount=data['amount'],
        date=data['date'],
        description=data['description'],
        category=category,
        user=user,
        transaction_type='Expense'
    )


@pytest.mark.django_db
def test_expense_add_nolog():
    client = Client()
    url = reverse('expense_add')
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('login') in response.url


@pytest.mark.django_db
def test_category_get(user, main_category, user_category, expense, income):
    client = Client()
    client.force_login(user)
    url = reverse('category')
    response = client.get(url)
    assert response.status_code == 200
    assert 'main_categories' in response.context
    assert 'main_stats' in response.context
    assert 'user_categories' in response.context
    assert 'user_stats' in response.context


@pytest.mark.django_db
def test_get_category_stats(user, user_category, expense, income):
    client = Client()
    client.force_login(user)
    url = reverse('category')
    response = client.get(url)
    stats = CategoryView().get_category_stats(user, [user_category])
    assert len(stats) == 1
    assert 'category' in stats[0]
    assert 'total_expense' in stats[0]
    assert 'total_income' in stats[0]
    assert stats[0]['category'] == user_category
    assert stats[0]['total_expense'] == Decimal('50.00')
    assert stats[0]['total_income'] == Decimal('100.00')


@pytest.mark.django_db
def test_category_nolog():
    client = Client()
    url = reverse('category')
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('login') in response.url


@pytest.mark.django_db
def test_category_add_get(user):
    client = Client()
    client.force_login(user)
    url = reverse('category_add')
    response = client.get(url)
    assert response.status_code == 200
    assert isinstance(response.context['form'], CategoryAddForm)


@pytest.mark.django_db
def test_category_add_post(user):
    client = Client()
    client.force_login(user)
    url = reverse('category_add')
    data = {'name': 'test',
            'description': 'test_description'}
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('category')
    assert Category.objects.get(name=data['name'], description=data['description'])


@pytest.mark.django_db
def test_category_add_nolog():
    client = Client()
    url = reverse('category_add')
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('login') in response.url


@pytest.mark.django_db
def test_category_delete_get(user, category):
    client = Client()
    client.force_login(user)
    url = reverse('category_delete', args=[category.id])
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['category'] == category


@pytest.mark.django_db
def test_category_delete_post(user, category):
    client = Client()
    client.force_login(user)
    url = reverse('category_delete', args=[category.id])
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('category')
    assert not Category.objects.filter(id=category.id).exists()


@pytest.mark.django_db
def test_category_delete_view_post_invalid(user):
    client = Client()
    client.force_login(user)
    url = reverse('category_delete', args=[999])
    response = client.post(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_category_delete_nolog(category):
    client = Client()
    url = reverse('category_delete', args=[category.id])
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('login') in response.url


@pytest.mark.django_db
def test_savings(saving, user):
    client = Client()
    client.force_login(user)
    url = reverse('savings')
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['savings'].count() == 2
    assert response.context['savings'][0].name == 'Test Savings'


@pytest.mark.django_db
def test_savings_nolog():
    client = Client()
    url = reverse('savings')
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('login') in response.url


@pytest.mark.django_db
def test_savings_edit_view_get(user, saving):
    client = Client()
    client.force_login(user)
    url = reverse('saving_edit', args=[saving[0].id])
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['form'].instance == saving[0]


@pytest.mark.django_db
def test_savings_edit_view_post(user, saving):
    client = Client()
    client.force_login(user)
    url = reverse('saving_edit', args=[saving[0].id])
    new_goal_amount = saving[0].goal_amount + 100
    data = {
        'user': user,
        'name': 'Test Savings',
        'end_date': '2022-12-31',
        'goal_amount': new_goal_amount
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('savings')
    updated_savings = Savings.objects.get(id=saving[0].id)
    assert updated_savings.goal_amount == new_goal_amount


@pytest.mark.django_db
def test_saving_edit_nolog(saving):
    client = Client()
    url = reverse('saving_edit', args=[saving[0].id])
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('login') in response.url


@pytest.mark.django_db
def test_savingsDelete_nolog(saving, user):
    client = Client()
    url = reverse('savings_delete', args=[saving[0].id])
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('login') in response.url


@pytest.mark.django_db
def test_savingsDelete():
    user = User.objects.create_user(username='test_user')
    saving = Savings.objects.create(user=user, name='Test Savings', end_date='2022-01-10', goal_amount=1000)
    client = Client()
    client.force_login(user)
    url = reverse('savings_delete', args=[saving.id])
    response = client.post(url)
    assert Savings.objects.filter(pk=saving.id).exists() is False
    assert response.status_code == 302
    assert response.url == reverse('savings')


@pytest.mark.django_db
def test_savingsAdd_get(user):
    client = Client()
    client.force_login(user)
    url = reverse('savings_add')
    response = client.get(url)
    assert response.status_code == 200
    assert isinstance(response.context['form'], SavingsAddForm)


@pytest.mark.django_db
def test_savingsAdd_post(user):
    client = Client()
    client.force_login(user)
    url = reverse('savings_add')
    data = {
        'name': 'Holidays',
        'end_date': '2022-01-10',
        'goal_amount': 1000,
        user: user.id
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert Savings.objects.get(
        name=data['name'],
        end_date=data['end_date'],
        goal_amount=data['goal_amount'],
        user=user
    )


@pytest.mark.django_db
def test_savings_add_nolog(saving):
    client = Client()
    url = reverse('savings_add')
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('login') in response.url


@pytest.mark.django_db
def test_AddMoneyToSavings(user):
    client = Client()
    client.force_login(user)
    saving = Savings.objects.create(user=user, name="Test Savings", end_date="2022-12-31", goal_amount=1000,
                                    current_amount=500, remaining_amount=500)
    url = reverse('add_money_to_savings', args=[saving.id])
    data = {'amount': 300}
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('savings')
    saving.refresh_from_db()
    assert saving.current_amount == 800
    assert saving.remaining_amount == 200


@pytest.mark.django_db
def test_AddMoneyToSavings_Error(user):
    client = Client()
    client.force_login(user)
    saving = Savings.objects.create(user=user, name="Test Savings", end_date="2022-12-31", goal_amount=1000,
                                    current_amount=500, remaining_amount=500)
    url = reverse('add_money_to_savings', args=[saving.id])
    data = {'amount': 800}
    response = client.post(url, data)
    assert response.status_code == 200
    assert saving.current_amount == 500
    assert saving.remaining_amount == 500
    assert 'Wprowadzona kwota przekracza pozostałą do osiągnięcia sumę.' in response.content.decode()


@pytest.mark.django_db
def test_add_money_to_savings_nolog(saving):
    client = Client()
    url = reverse('add_money_to_savings', args=[saving[0].id])
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('login') in response.url


@pytest.mark.django_db
def test_foreign_currency_list():
    client = Client()
    url = reverse('foreign_currencies')
    response = client.get(url)
    assert response.status_code == 200
    assert 'currencies' in response.context
    currencies = response.context['currencies']
    assert all(currencies[i].code <= currencies[i + 1].code for i in range(len(currencies) - 1))


@pytest.mark.django_db
def test_accounts_get(user, foreign_accounts):
    client = Client()
    client.force_login(user)
    url = reverse('accounts')
    response = client.get(url)
    assert response.status_code == 200
    assert 'accounts' in response.context
    assert response.context['accounts'].count() == len(foreign_accounts)
    for account in foreign_accounts:
        assert account in response.context['accounts']


@pytest.mark.django_db
def test_accounts_get_nolog():
    client = Client()
    url = reverse('accounts')
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('login') in response.url


@pytest.mark.django_db
def test_account_add_get(user):
    client = Client()
    client.force_login(user)
    url = reverse('account_add')
    response = client.get(url)
    assert response.status_code == 200
    assert isinstance(response.context['form'], AccountAddForm)


@pytest.mark.django_db
def test_account_add_post(user, zloty):
    client = Client()
    client.force_login(user)
    url = reverse('account_add')
    data = {
        'user': user.id,
        'name': 'test',
        'currency': zloty.id,
        'balance': 100,

    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('accounts')
    assert Account.objects.get(name=data['name'], currency=data['currency'], balance=data['balance'], user=data['user'])


@pytest.mark.django_db
def test_add_account_nolog():
    client = Client()
    url = reverse('account_add')
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('login') in response.url


@pytest.mark.django_db
def test_account_detail(user, foreign_accounts, transactions, foreign_currency):
    client = Client()
    client.force_login(user)
    url = reverse('account_details', args=[foreign_accounts[0].id])
    response = client.get(url)
    assert response.status_code == 200
    assert 'account' in response.context
    assert 'transactions' in response.context
    assert transactions[0].transaction_type == 'Income'
    assert foreign_accounts[0].name == 'AAA'
    assert len(transactions) == 1
    assert response.context['transactions'].count() == 1


@pytest.mark.django_db
def test_account_detail_nolog(foreign_accounts):
    client = Client()
    url = reverse('account_details', args=[foreign_accounts[0].id])
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('login') in response.url


@pytest.mark.django_db
def test_income_add_get(user, foreign_accounts):
    client = Client()
    client.force_login(user)
    url = reverse('for_income_add', args=[foreign_accounts[0].id])
    response = client.get(url)
    assert response.status_code == 200
    assert isinstance(response.context['form'], ForIncomeAddForm)


@pytest.mark.django_db
def test_income_add_post(user, foreign_accounts):
    client = Client()
    client.force_login(user)
    url = reverse('for_income_add', args=[foreign_accounts[0].id])
    data = {'amount': 100,
            'date': '2020-05-21',
            user: user.id
            }
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('account_details', args=[foreign_accounts[0].id])
    assert Transaction.objects.get(amount=data['amount'], date=data['date'], transaction_type='Income', user=user,
                                   currency=foreign_accounts[0].currency)
    updated_account = Account.objects.get(id=foreign_accounts[0].id)
    assert updated_account.balance == int(foreign_accounts[0].balance) + data['amount']


@pytest.mark.django_db
def test_income_add_nolog(foreign_accounts):
    client = Client()
    url = reverse('for_income_add', args=[foreign_accounts[0].id])
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('login') in response.url


@pytest.mark.django_db
def test_expense_add_get(user, foreign_accounts):
    client = Client()
    client.force_login(user)
    url = reverse('for_expense_add', args=[foreign_accounts[0].id])
    response = client.get(url)
    assert response.status_code == 200
    assert isinstance(response.context['form'], ForExpenseAddForm)


@pytest.mark.django_db
def test_expense_add_post_valid(user, foreign_accounts):
    client = Client()
    client.force_login(user)
    url = reverse('for_expense_add', args=[foreign_accounts[0].id])
    data = {'amount': 1,
            'date': '2020-05-21',
            user: user.id
            }
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('account_details', args=[foreign_accounts[0].id])
    assert Transaction.objects.get(amount=data['amount'], date=data['date'], transaction_type='Expense', user=user,
                                   currency=foreign_accounts[0].currency)
    updated_account = Account.objects.get(id=foreign_accounts[0].id)
    assert updated_account.balance == int(foreign_accounts[0].balance) - data['amount']


@pytest.mark.django_db
def test_expense_add_post_invalid(user, foreign_accounts):
    client = Client()
    client.force_login(user)
    url = reverse('for_expense_add', args=[foreign_accounts[0].id])
    data = {'amount': 100,
            'date': '2020-05-21',
            user: user.id
            }
    response = client.post(url, data)
    assert response.status_code == 200
    assert 'Nie można dodać wydatku większego niż saldo na koncie.' in response.content.decode()
    assert not Transaction.objects.filter(user=user, transaction_type='Expense').exists()
    updated_account = Account.objects.get(id=foreign_accounts[0].id)
    assert updated_account.balance == int(foreign_accounts[0].balance)


@pytest.mark.django_db
def test_expense_add_nolog(foreign_accounts):
    client = Client()
    url = reverse('for_expense_add', args=[foreign_accounts[0].id])
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('login') in response.url


@pytest.mark.django_db
def test_changetopln(user, foreign_accounts):
    client = Client()
    client.force_login(user)
    url = reverse('change_to_PLN', args=[foreign_accounts[0].id])
    data = {'amount': 100}
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('account_details', args=[foreign_accounts[0].id])
    updated_account = Account.objects.get(id=foreign_accounts[0].id)
    assert updated_account.balance == int(foreign_accounts[0].balance) - data['amount']
    assert Income.objects.get(user=user, amount=data['amount'] * int(foreign_accounts[0].currency.exchange_rate),
                              date=datetime.now())
    assert Transaction.objects.get(user=user, amount=data['amount'], transaction_type='Exchange',
                                   currency=foreign_accounts[0].currency, date=datetime.now())


@pytest.mark.django_db
def test_changetopln_nolog(foreign_accounts):
    client = Client()
    url = reverse('change_to_PLN', args=[foreign_accounts[0].id])
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('login') in response.url
