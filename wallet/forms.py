from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from wallet.models import Category, Income, Expense, Savings, Account


class LoginForm(forms.Form):
    username = forms.CharField(max_length=64, label='',
                               widget=forms.TextInput(attrs={'placeholder': 'Nazwa użytkownika'}))
    password = forms.CharField(max_length=64, label='', widget=forms.PasswordInput(attrs={'placeholder': 'Hasło'}))


class RegisterForm(forms.ModelForm):
    username = forms.CharField(max_length=64, label='',
                               widget=forms.TextInput(attrs={'placeholder': 'Nazwa użytkownika'}))
    password = forms.CharField(max_length=64, label='', widget=forms.PasswordInput(attrs={'placeholder': 'Hasło'}))

    class Meta:
        model = User
        fields = ['username']

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("re_password")
        if p1 is None or p2 is None or p1 != p2:
            raise ValidationError("Passwords don't match")
        return cleaned_data


class DateFilterForm(forms.Form):
    date_from = forms.DateField(label='Data od', widget=forms.TextInput(attrs={'type': 'date'}))
    date_to = forms.DateField(label='Data do', widget=forms.TextInput(attrs={'type': 'date'}))


class IncomeAddForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['amount', 'date', 'description', 'category']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }


class ExpenseAddForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'date', 'description', 'category']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }


class CategoryAddForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'


class SavingsAddForm(forms.ModelForm):
    class Meta:
        model = Savings
        fields = ['name', 'end_date', 'goal_amount', 'categories']
        widgets = {
            'end_date': forms.DateInput(attrs={'type': 'date'})
        }
    # def clean_goal_amount(self):
    #     goal_amount = self.cleaned_data['goal_amount']
    #     remaining_amount = self.cleaned_data.get('remaining_amount', 0)
    #
    #     if goal_amount > remaining_amount:
    #         raise forms.ValidationError('Wprowadzona kwota przekracza pozostałą do osiągnięcia sumę.')
    #
    #     return goal_amount


class AccountAddForm(forms.ModelForm):
    class Meta:
        model = Account
        exclude = ['user']


class ForIncomeAddForm(forms.Form):
    amount = forms.DecimalField(max_digits=20, decimal_places=2)
    date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))
    category = forms.ModelChoiceField(queryset=Category.objects)
