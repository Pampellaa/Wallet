from datetime import date, timedelta
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.db.models import Sum, Value, CharField
from django.shortcuts import render, redirect
from django.views import View

from wallet.forms import LoginForm, RegisterForm, DateFilterForm, IncomeAddForm, ExpenseAddForm, CategoryAddForm, \
    SavingsAddForm
from wallet.models import Income, Expense, Category, Savings


class IndexView(View):
    def get(self, request):

        return render(request, 'index.html' )

class DashboardView(View):
    def get(self, request):
        date30days = date.today() - timedelta(days=30)
        expense30days= Expense.objects.filter(user=request.user,date__gte=date30days).order_by('-date')
        sum_expenses = expense30days.aggregate(Sum('amount'))['amount__sum']
        income30days = Income.objects.filter(user=request.user,date__gte=date30days).order_by('-date')
        sum_income = income30days.aggregate(Sum('amount'))['amount__sum']
        together = sum_income - sum_expenses
        # expense30days = expense30days.annotate(transaction_type=Value('Expense', output_field=CharField()))
        # income30days = income30days.annotate(transaction_type=Value('Income', output_field=CharField()))
        # lastest = list(
        #     expense30days.values('transaction_type', 'amount', 'date') | income30days.values('transaction_type', 'amount', 'date')
        # )
        #
        # lastest.sort(key=lambda x: x['date'], reverse=True)
        return render(request, 'dash.html', {'sum_expenses': sum_expenses, 'sum_income':sum_income, 'together': together, 'lastest':lastest})

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


class IncomeView(View):
    def get(self, request):
        form = DateFilterForm()
        user = request.user
        incomes = Income.objects.filter(user=user).order_by('-date')
        total_income = incomes.aggregate(Sum('amount'))['amount__sum']
        return render(request, 'income.html', {'incomes': incomes, 'total_income': total_income,'form':form})
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


class IncomeAddView(View):
    def get(self, request):
        form = IncomeAddForm()
        return render(request, 'add_form.html', {'form': form})
    def post(self, request):
        form = IncomeAddForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('income')
        return render(request, 'income.html', {'form': form})


class ExpenseView(View):
    def get(self, request):
        form = DateFilterForm()
        user = request.user
        expenses = Expense.objects.filter(user=user).order_by('-date')
        total_expense = expenses.aggregate(Sum('amount'))['amount__sum']
        return render(request, 'expense.html', {'expenses': expenses, 'total_expense': total_expense,'form':form})
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


class ExpenseAddView(View):
    def get(self, request):
        form = ExpenseAddForm()
        return render(request, 'add_form.html', {'form': form})
    def post(self, request):
        form = ExpenseAddForm(request.POST)
        if form.is_valid():
            expense = form.save()
            return redirect('expense')
        return render(request, 'expense.html', {'form': form})

class CategoryView(View):
    def get(self, request):
        categories = Category.objects.all()
        return render(request, 'category.html', {'categories':categories})


class CategoryAddView(View):
    def get(self, request):
        form = CategoryAddForm()
        return render(request, 'add_form.html', {'form':form})
    def post(self,request):
        form = CategoryAddForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category')
        return render(request, 'category.html', {'form':form})

class SavingsView(View):
    def get(self, request):
        savings = Savings.objects.filter(user=request.user)
        return render(request, 'savings.html', {'savings':savings})

class SavingsAddView(View):
    def get(self, request):
        form = SavingsAddForm()
        return render(request, 'add_form.html', {'form':form})
    def post(self,request):
        form = SavingsAddForm(request.POST)
        if form.is_valid():
            savings = form.save(commit=False)
            savings.user = request.user
            form.save()
            return redirect('savings')
        return render(request, 'savings.html', {'form':form})

class SavingsDeleteView(View):
    def post(self, request, saving_id):
        saving = Savings.objects.get(pk=saving_id)
        saving.delete()
        return redirect('savings')


class AddMoneyToSavingsView(View):
    def post(self, request, saving_id):
        amount = Decimal(request.POST.get('amount'))
        savings_goal = Savings.objects.get(id=saving_id)

        if amount <= savings_goal.remaining_amount:
            savings_goal.current_amount += amount
            savings_goal.save()
            return redirect('savings')
        else:
            error_message = 'Wprowadzona kwota przekracza pozostałą do osiągnięcia sumę.'
            savings_list = Savings.objects.all()
            return render(request, 'savings.html', {'error_message': error_message, 'savings': savings_list, 'invalid_saving_id': saving_id})

