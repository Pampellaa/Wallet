from datetime import date, timedelta, datetime
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from wallet.forms import LoginForm, RegisterForm, IncomeExpenseAddForm, CategoryAddForm, \
    SavingsAddForm, AccountAddForm, ForIncomeAddForm, ForExpenseAddForm, CurrencySearchform, \
    IncomeExpenseFilterForm
from wallet.models import Income, Expense, Category, Savings, Transaction, Account, Currency


class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')


class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        date30days = date.today() - timedelta(days=30)
        today = date.today()
        expense30days = Expense.objects.filter(user=request.user, date__gte=date30days).order_by('-date')
        # calkowita suma pola 'amount' dla obiektów Expense z ostatnich 30 dni:
        sum_expenses = expense30days.aggregate(Sum('amount'))['amount__sum']
        sum_expenses_round = 0
        if sum_expenses is not None:
            sum_expenses_round = round(sum_expenses, 0)

        try:
            category = Category.objects.get(name='wymiana')
        except Category.DoesNotExist:
            category = None
        income30days = Income.objects.filter(user=request.user, date__gte=date30days).exclude(
            category=category).order_by('-date')
        sum_income = income30days.aggregate(Sum('amount'))['amount__sum']

        sum_income_round = 0
        if sum_income is not None:
            sum_income_round = round(sum_income, 0)

        if sum_income is not None and sum_expenses is not None:
            together = round(sum_income - sum_expenses, 2)
        else:
            together = None

        account = Account.objects.filter(user=request.user)

        transactionsPLN = Transaction.objects.filter(user=request.user, date__gte=date30days, currency=153).order_by(
            '-date')
        transactionsFOR = Transaction.objects.filter(user=request.user, date__gte=date30days).exclude(
            currency=153).order_by('-date')
        transactionsEXC = Transaction.objects.filter(user=request.user, date__gte=date30days,
                                                     transaction_type='Exchange').order_by('-date')[:10]
        for transaction in transactionsEXC:
            exchange_rate = transaction.currency.exchange_rate
            transaction.change_in_PLN = round(transaction.amount * exchange_rate, 2)

        return render(request, 'dash.html',
                      {'sum_expenses': sum_expenses, 'sum_income': sum_income, 'together': together,
                       'transactionsPLN': transactionsPLN, 'transactionsFOR': transactionsFOR, 'account': account,
                       'sum_expenses_round': sum_expenses_round, 'sum_income_round': sum_income_round,
                       'transactionsEXC': transactionsEXC, 'date30days': date30days, 'today': today})


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
        form.add_error('username', 'Nieprawidłowe dane logowania. Spróbuj ponownie.')
        return render(request, 'login.html', {'form': form})


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
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = User.objects.create(username=username)
            user.set_password(password)
            user.save()
            login(request, user)
            return redirect('login')
        return render(request, 'register.html', {'form': form})


class IncomeView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        built_in_categories = Category.objects.filter(is_built=True)
        user_categories = Category.objects.filter(user=user, is_built=False)
        all_categories = built_in_categories | user_categories
        form2 = IncomeExpenseFilterForm(categories=all_categories)
        incomes = Income.objects.filter(user=user).order_by('-date')

        total_income = 0
        if incomes.exists():
            total_income = round(incomes.aggregate(Sum('amount'))['amount__sum'], 2)

        return render(request, 'income.html',
                      {'incomes': incomes, 'total_income': total_income, 'form2': form2})

    def post(self, request):
        user = request.user
        built_in_categories = Category.objects.filter(is_built=True)
        user_categories = Category.objects.filter(user=user, is_built=False)
        all_categories = built_in_categories | user_categories
        form2 = IncomeExpenseFilterForm(request.POST, categories=all_categories)
        incomes = Income.objects.filter(user=user)

        if form2.is_valid():
            date_from = form2.cleaned_data['date_from']
            date_to = form2.cleaned_data['date_to']
            category = form2.cleaned_data['category']

            if date_from:
                incomes = incomes.filter(date__gte=date_from)
            if date_to:
                incomes = incomes.filter(date__lte=date_to)
            if category:
                incomes = incomes.filter(category=category)

            total_income = 0
            if incomes.exists():
                total_income = round(incomes.aggregate(Sum('amount'))['amount__sum'], 2)

            return render(request, 'income.html',  {'incomes': incomes, 'total_income': total_income, 'form2': form2})
        return render(request, 'add_form.html', {'form2': form2})


class IncomeAddView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        built_in_categories = Category.objects.filter(is_built=True)
        user_categories = Category.objects.filter(user=user, is_built=False)
        all_categories = built_in_categories | user_categories
        form = IncomeExpenseAddForm(categories=all_categories)
        return render(request, 'add_form.html', {'form': form})

    def post(self, request):
        form = IncomeExpenseAddForm(request.POST, categories=Category.objects.all())
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
        return render(request, 'add_form.html', {'form': form})


class ExpenseView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        built_in_categories = Category.objects.filter(is_built=True)
        user_categories = Category.objects.filter(user=user, is_built=False)
        all_categories = built_in_categories | user_categories
        form2 = IncomeExpenseFilterForm(categories=all_categories)
        expenses = Expense.objects.filter(user=user).order_by('-date')

        total_expense = 0
        if expenses.exists():
            total_expense = expenses.aggregate(Sum('amount'))['amount__sum']

        return render(request, 'expense.html', {'expenses': expenses, 'total_expense': total_expense, 'form2': form2})

    def post(self, request):
        user = request.user
        built_in_categories = Category.objects.filter(is_built=True)
        user_categories = Category.objects.filter(user=user, is_built=False)
        all_categories = built_in_categories | user_categories
        form2 = IncomeExpenseFilterForm(request.POST, categories=all_categories)
        expenses = Expense.objects.filter(user=user)
        if form2.is_valid():
            date_from = form2.cleaned_data['date_from']
            date_to = form2.cleaned_data['date_to']
            category = form2.cleaned_data['category']

            if date_from:
                expenses = expenses.filter(date__gte=date_from)

            if date_to:
                expenses = expenses.filter(date__lte=date_to)
            if category:
                expenses = expenses.filter(category=category)

            total_expense = 0
            if expenses.exists():
                total_expense = expenses.aggregate(Sum('amount'))['amount__sum']

            return render(request, 'expense.html', {'expenses': expenses, 'total_expense': total_expense, 'form2': form2})
        return render(request, 'add_form.html', {'form2': form2})


class ExpenseAddView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        built_in_categories = Category.objects.filter(is_built=True)
        user_categories = Category.objects.filter(user=user, is_built=False)
        all_categories = built_in_categories | user_categories
        form = IncomeExpenseAddForm(categories=all_categories)
        return render(request, 'add_form.html', {'form': form})

    def post(self, request):
        form = IncomeExpenseAddForm(request.POST, categories=Category.objects.all())
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
                transaction_type='Expense',
            )
            Expense.objects.create(
                user=user,
                amount=amount,
                date=date,
                description=description,
                category=category,
            )
            return redirect('expense')
        return render(request, 'add_form.html', {'form': form})


class CategoryView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        main_categories = Category.objects.filter(is_built=True)
        user_categories = Category.objects.filter(is_built=False, user=user)
        date30days = date.today() - timedelta(days=30)
        today = date.today()
        main_stats = self.get_category_stats(user, main_categories)
        user_stats = self.get_category_stats(user, user_categories)

        return render(request, 'category.html', {'main_categories': main_categories, 'main_stats': main_stats,
                                                 'user_categories': user_categories, 'user_stats': user_stats,
                                                 'date30days': date30days, 'today': today})

    def get_category_stats(self, user, categories):
        stats = []
        date30days = date.today() - timedelta(days=30)
        for category in categories:
            total_expense = Expense.objects.filter(
                user=user,
                category=category,
                date__gte=date30days
            ).aggregate(Sum('amount'))['amount__sum'] or 0

            total_income = Income.objects.filter(
                user=user,
                category=category,
                date__gte=date30days
            ).aggregate(Sum('amount'))['amount__sum'] or 0

            stats.append({
                'category': category,
                'total_expense': round(total_expense, 2),
                'total_income': round(total_income, 2)
            })
        return stats


class CategoryAddView(LoginRequiredMixin, View):
    def get(self, request):
        form = CategoryAddForm()
        return render(request, 'add_form.html', {'form': form})

    def post(self, request):
        form = CategoryAddForm(request.POST, user=request.user)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            Category.objects.create(user=request.user, name=name, description=description, is_built=False)
            return redirect('category')
        return render(request, 'category.html', {'form': form})


class CategoryDeleteView(LoginRequiredMixin, View):
    def get(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        return render(request, 'delete_confirmation.html', {'category': category})

    def post(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        category.delete()
        return redirect('category')


class SavingsView(LoginRequiredMixin, View):
    def get(self, request):
        savings = Savings.objects.filter(user=request.user)
        return render(request, 'savings.html', {'savings': savings})

# saving sprawia że dane z obiektu są wpisane w pola formularza a po zatwierdzeniu zastosowane beda zmiany do tego konkretnego elementu
class SavingsEditView(LoginRequiredMixin, View):
    def get(self, request, saving_id):
        saving = Savings.objects.get(user=request.user, id=saving_id)
        form = SavingsAddForm(instance=saving)
        return render(request, 'add_form.html', {'form': form})

    def post(self, request, saving_id):
        user = request.user
        saving = Savings.objects.get(user=user, id=saving_id)
        form = SavingsAddForm(request.POST, instance=saving)
        if form.is_valid():
            form.save()
            return redirect('savings')
        return render(request, 'add_form.html', {'form': form})


class SavingsAddView(LoginRequiredMixin, View):
    def get(self, request):
        form = SavingsAddForm()
        return render(request, 'add_form.html', {'form': form})

    def post(self, request):
        form = SavingsAddForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            return redirect('savings')
        return render(request, 'add_form.html', {'form': form})


class SavingsDeleteView(LoginRequiredMixin, View):
    def post(self, request, saving_id):
        saving = Savings.objects.get(id=saving_id)
        saving.delete()
        return redirect('savings')


class AddMoneyToSavingsView(LoginRequiredMixin, View):
    def post(self, request, saving_id):
        amount = Decimal(request.POST.get('amount'))
        savings_goal = Savings.objects.get(id=saving_id, user=request.user)

        if amount <= savings_goal.remaining_amount:
            savings_goal.current_amount += amount
            savings_goal.remaining_amount -= amount
            savings_goal.save()
            return redirect('savings')

        error_message = 'Wprowadzona kwota przekracza pozostałą do osiągnięcia sumę.'
        savings_list = Savings.objects.filter(user=request.user)
        return render(request, 'savings.html',
                      {'error_message': error_message, 'savings': savings_list, 'invalid_saving_id': saving_id})


class ForeignCurrenciesView(LoginRequiredMixin, View):
    def get(self, request):
        # pobiera parametr 'sort_order' z parametrów żądania GET, jeśli nie istnieje, używana jest domyślna wartość code
        sort_order = request.GET.get('sort_order', 'code')
        currencies = Currency.objects.all().order_by(sort_order)
        form = CurrencySearchform(request.GET)
        if form.is_valid():
            name = form.cleaned_data.get('name', '')
            currencies = currencies.filter(name__icontains=name)
        return render(request, 'currency.html', {'currencies': currencies, 'sort_order': sort_order, 'form': form})


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
            form.instance.user = request.user
            form.save()
            return redirect('accounts')
        return render(request, 'add_form.html', {'form': form})


class AccountDeleteView(LoginRequiredMixin, View):
    def post(self, request, account_id):
        account = Account.objects.get(id=account_id)
        account.delete()
        return redirect('accounts')


class AccountDetailsView(LoginRequiredMixin, View):
    def get(self, request, account_id):
        account = Account.objects.get(id=account_id, user=request.user)
        transactions = Transaction.objects.filter(currency_id=account.currency_id, user=request.user).order_by('-date')
        for transaction in transactions:
            if transaction.transaction_type == 'Income':
                transaction.transaction_type = 'Wpływ'
            else:
                transaction.transaction_type = 'Wydatek'
        return render(request, 'account_details.html', {"account": account, 'transactions': transactions})


class ForIncomeView(LoginRequiredMixin, View):
    def get(self, request, account_id):
        user = request.user
        built_in_categories = Category.objects.filter(is_built=True)
        user_categories = Category.objects.filter(user=user, is_built=False)
        all_categories = built_in_categories | user_categories
        form = ForIncomeAddForm(categories=all_categories)
        return render(request, 'add_form.html', {'form': form})

    def post(self, request, account_id):
        form = ForIncomeAddForm(request.POST, categories=Category.objects.all())
        if form.is_valid():
            user = request.user
            new_amount = form.cleaned_data['amount']
            category = form.cleaned_data['category']
            date = form.cleaned_data['date']
            account = Account.objects.get(id=account_id)
            account.balance += int(new_amount)
            account.save()
            currency = account.currency
            Transaction.objects.create(
                user=user,
                transaction_type='Income',
                currency=currency,
                category=category,
                date=date,
                amount=new_amount)
            return redirect('account_details', account.id)
        return render(request, 'add_form.html', {'form': form})


class ForExpenseView(LoginRequiredMixin, View):
    def get(self, request, account_id):
        user = request.user
        built_in_categories = Category.objects.filter(is_built=True)
        user_categories = Category.objects.filter(user=user, is_built=False)
        all_categories = built_in_categories | user_categories
        form = ForExpenseAddForm(categories=all_categories)
        return render(request, 'add_form.html', {'form': form})

    def post(self, request, account_id):
        form = ForExpenseAddForm(request.POST, categories=Category.objects.all())
        if form.is_valid():
            user = request.user
            new_amount = form.cleaned_data['amount']
            category = form.cleaned_data['category']
            date = form.cleaned_data['date']
            account = Account.objects.get(id=account_id)
            if new_amount > account.balance:
                form.add_error('amount', "Nie można dodać wydatku większego niż saldo na koncie.")
                return render(request, 'add_form.html', {'form': form})
            account.balance -= int(new_amount)
            account.save()
            currency = account.currency
            Transaction.objects.create(
                user=user,
                transaction_type='Expense',
                currency=currency,
                category=category,
                date=date,
                amount=new_amount)
            return redirect('account_details', account_id)
        return render(request, 'add_form.html', {'form': form})


class ChangeToPLNView(LoginRequiredMixin, View):
    def post(self, request, account_id):
        amount = Decimal(request.POST.get('amount'))
        account = Account.objects.get(id=account_id)
        if amount > account.balance:
            messages.info(request, "Nie można wymienić więcej niż dostępne saldo na koncie.")
            return redirect('account_details', account_id)

        real_amount = int(amount) * Decimal(account.currency.exchange_rate)
        category = Category.objects.get(name='Wymiana')
        Income.objects.create(user=request.user, amount=real_amount, date=datetime.now(), category=category)
        Transaction.objects.create(user=request.user, amount=amount, transaction_type='Exchange',
                                   currency=account.currency, date=datetime.now())
        account.balance -= int(amount)
        account.save()
        return redirect('account_details', account_id)
