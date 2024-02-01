from datetime import date, timedelta, datetime
from decimal import Decimal
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.views import View
from wallet.forms import LoginForm, RegisterForm, DateFilterForm, IncomeAddForm, ExpenseAddForm, CategoryAddForm, \
    SavingsAddForm, AccountAddForm, ForIncomeAddForm
from wallet.models import Income, Expense, Category, Savings, Transaction, Account, Currency


class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')


class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        date30days = date.today() - timedelta(days=30)
        expense30days = Expense.objects.filter(user=request.user, date__gte=date30days).order_by('-date')
        sum_expenses = expense30days.aggregate(Sum('amount'))['amount__sum']
        income30days = Income.objects.filter(user=request.user, date__gte=date30days).order_by('-date')
        sum_income = income30days.aggregate(Sum('amount'))['amount__sum']
        if sum_income is not None and sum_expenses is not None:
            together = round(sum_income - sum_expenses, 2)
        else:
            together = None

        account = Account.objects.filter(user=request.user)

        transactionsPLN = Transaction.objects.filter(user=request.user, date__gte=date30days, currency=153).order_by(
            '-date')
        transactionsFOR = Transaction.objects.filter(user=request.user, date__gte=date30days).exclude(
            currency=153).order_by('-date')
        return render(request, 'dash.html',
                      {'sum_expenses': sum_expenses, 'sum_income': sum_income, 'together': together,
                       'transactionsPLN': transactionsPLN, 'transactionsFOR': transactionsFOR, 'account': account})


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'login2.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
        return render(request, 'login2.html', {'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('index')


class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password'))
            user.save()
            login(request, user)
            return redirect('login')
        return render(request, 'register.html', {'form': form})

#2 testy
class IncomeView(LoginRequiredMixin, View):
    def get(self, request):
        form = DateFilterForm()
        user = request.user
        incomes = Income.objects.filter(user=user).order_by('-date')
        total_income = incomes.aggregate(Sum('amount'))['amount__sum']
        if total_income is not None:
            total_income = round(total_income, 2)
        else:
            total_income = 0
        return render(request, 'income.html', {'incomes': incomes, 'total_income': total_income, 'form': form})

    def post(self, request):
        form = DateFilterForm(request.POST)
        if form.is_valid():
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            user = request.user
            incomes = Income.objects.filter(user=user)

            if date_from:
                incomes = incomes.filter(date__gte=date_from)

            if date_to:
                incomes = incomes.filter(date__lte=date_to)

            total_income = incomes.aggregate(Sum('amount'))['amount__sum']

            context = {'incomes': incomes, 'total_income': total_income, 'form': form}
            return render(request, 'income.html', context)

        context = {'form': form}
        return render(request, 'income.html', context)

#2 testy
class IncomeAddView(LoginRequiredMixin, View):
    def get(self, request):
        form = IncomeAddForm()
        return render(request, 'add_form.html', {'form': form})

    def post(self, request):
        form = IncomeAddForm(request.POST)
        if form.is_valid():
            user = request.user
            amount = form.cleaned_data['amount']
            date = form.cleaned_data['date']
            description = form.cleaned_data['description']
            category = form.cleaned_data['category']
            Transaction.objects.create(
                user=user,
                amount=amount,
                date=date,
                description=description,
                category=category,
                transaction_type='Income',
            )
            Income.objects.create(
                user=user,
                amount=amount,
                date=date,
                description=description,
                category=category,
            )
            return redirect('income')
        return render(request, 'income.html', {'form': form})

#2 testy
class ExpenseView(LoginRequiredMixin, View):
    def get(self, request):
        form = DateFilterForm()
        user = request.user
        expenses = Expense.objects.filter(user=user).order_by('-date')

        total_expense = expenses.aggregate(Sum('amount'))['amount__sum']
        if total_expense is not None:
            total_expense = round(total_expense, 2)
        else:
            total_expense = 0
        return render(request, 'expense.html', {'expenses': expenses, 'total_expense': total_expense, 'form': form})

    def post(self, request):
        form = DateFilterForm(request.POST)
        if form.is_valid():
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            user = request.user
            expenses = Expense.objects.filter(user=user)

            if date_from:
                expenses = expenses.filter(date__gte=date_from)

            if date_to:
                expenses = expenses.filter(date__lte=date_to)

            total_expense = expenses.aggregate(Sum('amount'))['amount__sum']

            context = {'expenses': expenses, 'total_expense': total_expense, 'form': form}
            return render(request, 'expense.html', context)

        context = {'form': form}
        return render(request, 'expense.html', context)

#2 testy
class ExpenseAddView(LoginRequiredMixin, View):
    def get(self, request):
        form = ExpenseAddForm()
        return render(request, 'add_form.html', {'form': form})

    def post(self, request):
        form = ExpenseAddForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            date = form.cleaned_data['date']
            description = form.cleaned_data['description']
            category = form.cleaned_data['category']
            Transaction.objects.create(
                user=request.user,
                amount=amount,
                date=date,
                description=description,
                category=category,
                transaction_type='Expense',
            )
            Expense.objects.create(
                user=request.user,
                amount=amount,
                date=date,
                description=description,
                category=category,
            )
            return redirect('expense')
        return render(request, 'expense.html', {'form': form})


class CategoryView(LoginRequiredMixin, View):
    def get(self, request):
        categories = Category.objects.all()
        return render(request, 'category.html', {'categories': categories})


class CategoryAddView(LoginRequiredMixin, View):
    def get(self, request):
        form = CategoryAddForm()
        return render(request, 'add_form.html', {'form': form})

    def post(self, request):
        form = CategoryAddForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category')
        return render(request, 'category.html', {'form': form})

#2 testy
class SavingsView(LoginRequiredMixin, View):
    def get(self, request):
        savings = Savings.objects.filter(user=request.user)
        return render(request, 'savings.html', {'savings': savings})

#2 testy
class SavingsAddView(LoginRequiredMixin, View):
    def get(self, request):
        form = SavingsAddForm()
        return render(request, 'add_form.html', {'form': form})

    def post(self, request):
        form = SavingsAddForm(request.POST)
        if form.is_valid():
            savings = form.save(commit=False)
            savings.user = request.user
            form.save()
            return redirect('savings')
        return render(request, 'savings.html', {'form': form})

#2 testy
class SavingsDeleteView(LoginRequiredMixin, View):
    def post(self, request, saving_id):
        saving = Savings.objects.get(pk=saving_id)
        saving.delete()
        return redirect('savings')

#2 testy
class AddMoneyToSavingsView(LoginRequiredMixin, View):
    def post(self, request, saving_id):
        amount = Decimal(request.POST.get('amount'))
        savings_goal = Savings.objects.get(id=saving_id)

        if amount <= savings_goal.remaining_amount:
            savings_goal.current_amount += amount
            savings_goal.remaining_amount -= amount
            savings_goal.save()
            return redirect('savings')
        else:
            error_message = 'Wprowadzona kwota przekracza pozostałą do osiągnięcia sumę.'
            savings_list = Savings.objects.all()
            return render(request, 'savings.html',
                          {'error_message': error_message, 'savings': savings_list, 'invalid_saving_id': saving_id})


class ForeignCurrenciesView(LoginRequiredMixin, View):
    def get(self, request):
        currencies = Currency.objects.all().order_by('code')
        return render(request, 'currency.html', {"currencies": currencies})


class AccountsView(LoginRequiredMixin, View):
    def get(self, request):
        accounts = Account.objects.filter(user=request.user)
        return render(request, 'accounts.html', {'accounts': accounts})


class AccountAddView(LoginRequiredMixin, View):
    def get(self, request):
        form = AccountAddForm()
        return render(request, 'add_form.html', {'form': form})

    def post(self, request):
        form = AccountAddForm(request.POST)
        if form.is_valid():
            user = request.user
            form.save()
            return redirect('accounts')
        return render(request, 'accounts.html', {'form': form})


class AccountDetailsView(LoginRequiredMixin, View):
    def get(self, request, account_id):
        account = Account.objects.get(id=account_id, user=request.user)
        transactions = Transaction.objects.filter(currency_id=account.currency_id)
        return render(request, 'account_details.html', {"account": account, 'transactions': transactions})


class ForIncomeView(LoginRequiredMixin, View):
    def get(self, request, account_id):
        form = ForIncomeAddForm()
        return render(request, 'add_form.html', {'form': form})

    def post(self, request, account_id):
        form = ForIncomeAddForm(request.POST)
        if form.is_valid():
            user = request.user
            new_amount = form.cleaned_data['amount']
            category = form.cleaned_data['category']
            date = form.cleaned_data['date']
            account = Account.objects.get(id=account_id)
            account.balance += int(new_amount)
            account.save()
            currency = account.currency
            new_transaction = Transaction.objects.create(
                amount=new_amount,
                user=request.user,
                date=date,
                category=category,
                transaction_type='Income',
                currency=currency
            )
            return redirect('accounts')
        return render(request, 'add_form.html', {'form': form})


class ForExpenseView(LoginRequiredMixin, View):
    def get(self, request, account_id):
        form = ForIncomeAddForm()
        return render(request, 'add_form.html', {'form': form})

    def post(self, request, account_id):
        form = ForIncomeAddForm(request.POST)
        if form.is_valid():
            user = request.user
            new_amount = form.cleaned_data['amount']
            category = form.cleaned_data['category']
            date = form.cleaned_data['date']
            account = Account.objects.get(id=account_id)
            account.balance -= int(new_amount)
            account.save()
            currency = account.currency
            new_transaction = Transaction.objects.create(
                amount=new_amount,
                user=request.user,
                date=date,
                category=category,
                transaction_type='Expense',
                currency=currency
            )
            return redirect('accounts')
        return render(request, 'add_form.html', {'form': form})


class change_to_PLNView(LoginRequiredMixin, View):
    def post(self, request, account_id):
        amount = Decimal(request.POST.get('amount'))
        account = Account.objects.get(id=account_id)
        real_amount = int(amount) * Decimal(account.currency.exchange_rate)
        Income.objects.create(user=request.user, amount=real_amount, date=datetime.now())
        Transaction.objects.create(user=request.user, amount=amount, transaction_type='Exchange',
                                   currency=account.currency, date=datetime.now())
        account.balance -= int(amount)
        account.save()
        return redirect('accounts')
