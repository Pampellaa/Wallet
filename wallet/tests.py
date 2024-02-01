import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User

from wallet.forms import IncomeAddForm, ExpenseAddForm, SavingsAddForm
from wallet.models import Income, Category, Transaction, Expense, Savings


@pytest.mark.django_db
def test_status():
    assert True

@pytest.mark.django_db
def test_income(income):
    user, incomes = income
    client = Client()
    client.force_login(user)
    url = reverse('income')
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['incomes'].count() == 3
    expected_total_income = sum(income.amount for income in incomes)
    assert response.context['total_income'] == expected_total_income

@pytest.mark.django_db
def test_income2(income2):
    income, post_data = income2
    user, incomes = income
    client = Client()
    client.force_login(user)
    url = reverse('income')
    response = client.post(url, data=post_data)
    assert response.status_code == 200
    assert response.context['incomes'].count() == 2
    expected_total_income = 50 + 100
    assert response.context['total_income'] == expected_total_income

@pytest.mark.django_db
def test_expense(expense):
    user, expenses = expense
    client = Client()
    client.force_login(user)
    url = reverse('expense')
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['expenses'].count() == 3
    expected_total_expense = sum(expense.amount for expense in expenses)
    assert response.context['total_expense'] == expected_total_expense

@pytest.mark.django_db
def test_expense2(expense2):
    expense, post_data = expense2
    user, expenses = expense
    client = Client()
    client.force_login(user)
    url = reverse('expense')
    response = client.post(url, data=post_data)
    assert response.status_code == 200
    assert response.context['expenses'].count() == 2
    expected_total_expense = 50 + 100
    assert response.context['total_expense'] == expected_total_expense

@pytest.mark.django_db
def test_incomeAdd_get():
    user = User.objects.create(username='test_user')
    client = Client()
    client.force_login(user)
    url = reverse('income_add')
    response = client.get(url)
    assert response.status_code == 200
    assert isinstance(response.context['form'], IncomeAddForm)

@pytest.mark.django_db
def test_incomeAdd_post(zloty):
    category = Category.objects.create(name='Test Category')
    user = User.objects.create(username='test_user')
    client = Client()
    client.force_login(user)
    url = reverse('income_add')
    data = {
        'amount':100,
        'date': '2020-05-21',
        'description': 'test description',
        'category': category.id,
        'user': user.id
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert Income.objects.get(
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
        transaction_type='Income'
    )

@pytest.mark.django_db
def test_expenseAdd_get():
    user = User.objects.create(username='test_user')
    client = Client()
    client.force_login(user)
    url = reverse('expense_add')
    response = client.get(url)
    assert response.status_code == 200
    assert isinstance(response.context['form'], ExpenseAddForm)

@pytest.mark.django_db
def test_expenseAdd_post(zloty):
    category = Category.objects.create(name='Test Category')
    user = User.objects.create(username='test_user')
    client = Client()
    client.force_login(user)
    url = reverse('expense_add')
    data = {
        'amount':100,
        'date': '2020-05-21',
        'description': 'test description',
        'category': category.id,
        'user': user.id
    }
    response = client.post(url, data)
    assert response.status_code == 302
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
def test_savings(saving):
    user, savings = saving
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
def test_savingsDelete_nolog():
    user = User.objects.create_user(username='test_user')
    saving = Savings.objects.create(user=user, name='Test Savings', end_date='2022-01-10', goal_amount=1000)
    client = Client()
    url = reverse('savings_delete', args=[saving.id])
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
def test_savingsAdd_get():
    user = User.objects.create(username='test_user')
    client = Client()
    client.force_login(user)
    url = reverse('savings_add')
    response = client.get(url)
    assert response.status_code == 200
    assert isinstance(response.context['form'], SavingsAddForm)

@pytest.mark.django_db
def test_savingsAdd_post():
    user = User.objects.create(username='test_user')
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
def test_AddMoneyToSavings():
    user = User.objects.create(username="test_user")
    client = Client()
    client.force_login(user)
    saving = Savings.objects.create(user=user, name="Test Savings", end_date="2022-12-31", goal_amount=1000, current_amount=500, remaining_amount=500)
    url = reverse('add_money_to_savings', args=[saving.id])
    data = {'amount': 300}
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('savings')
    saving.refresh_from_db()
    assert saving.current_amount == 800
    assert saving.remaining_amount == 200

@pytest.mark.django_db
def test_AddMoneyToSavings_Error():
    user = User.objects.create(username="test_user")
    client = Client()
    client.force_login(user)
    saving = Savings.objects.create(user=user, name="Test Savings", end_date="2022-12-31", goal_amount=1000, current_amount=500, remaining_amount=500)
    url = reverse('add_money_to_savings', args=[saving.id])
    data = {'amount': 800}
    response = client.post(url, data)
    assert response.status_code == 200
    assert saving.current_amount == 500
    assert saving.remaining_amount == 500
    assert 'Wprowadzona kwota przekracza pozostałą do osiągnięcia sumę.' in response.content.decode()