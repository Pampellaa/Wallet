from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from wallet.models import Category, Income, Expense, Savings, Account, Transaction


class LoginForm(forms.Form):
    username = forms.CharField(max_length=64, label='',
                               widget=forms.TextInput(attrs={'placeholder': 'Nazwa użytkownika'}))
    password = forms.CharField(max_length=64, label='', widget=forms.PasswordInput(attrs={'placeholder': 'Hasło'}))


class RegisterForm(forms.ModelForm):

    password1 = forms.CharField(max_length=64, label='', widget=forms.PasswordInput(attrs={'placeholder': 'Hasło'}))
    password2 = forms.CharField(max_length=64, label='',
                                widget=forms.PasswordInput(attrs={'placeholder': 'Potwierdź hasło'}))
    class Meta:
        model = User
        fields = ('username',)
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Hasła nie pasują do siebie.')

        return password2


class DateFilterForm(forms.Form):
    date_from = forms.DateField(label='Data od', widget=forms.TextInput(attrs={'type': 'date'}), input_formats=['%Y-%m-%d', '%d.%m.%Y', '%d-%m-%Y'])
    date_to = forms.DateField(label='Data do', widget=forms.TextInput(attrs={'type': 'date'}), input_formats=['%Y-%m-%d', '%d.%m.%Y', '%d-%m-%Y'])


class IncomeAddForm(forms.ModelForm):

    class Meta:
        model = Income
        fields = ['amount', 'date', 'description', 'category']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),

        }
        labels = {
            'amount': 'Kwota',
            'date': 'Data',
            'description': 'Opis',
            'category': 'Kategoria',
        }
    def __init__(self, *args, **kwargs):
        categories = kwargs.pop('categories', None)
        super(IncomeAddForm, self).__init__(*args, **kwargs)
        if categories:
            self.fields['category'].queryset = categories



class ExpenseAddForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'date', 'description', 'category']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }
        labels = {
            'amount': 'Kwota',
            'date': 'Data',
            'description': 'Opis',
            'category': 'Kategoria',
        }
    def __init__(self, *args, **kwargs):
        categories = kwargs.pop('categories', None)
        super(ExpenseAddForm, self).__init__(*args, **kwargs)
        if categories:
            self.fields['category'].queryset = categories


class CategoryAddForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'is_built']
    def __init__(self, *args, user=None, **kwargs):
        super(CategoryAddForm, self).__init__(*args, **kwargs)
        self.fields['is_built'].widget = forms.HiddenInput()
        if user is not None:
            self.instance.user = user


class SavingsAddForm(forms.ModelForm):
    class Meta:
        model = Savings
        fields = ['name', 'end_date', 'goal_amount', 'categories']
        widgets = {
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'categories': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'name': 'Nazwa',
            'end_date': 'Data zakończenia',
            'goal_amount': 'Cel',
            'categories': 'Kategorie'
        }



class AccountAddForm(forms.ModelForm):
    class Meta:
        model = Account
        exclude = ['user']


class ForIncomeAddForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'date', 'category']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        categories = kwargs.pop('categories', None)
        super(ForIncomeAddForm, self).__init__(*args, **kwargs)
        if categories:
            self.fields['category'].queryset = categories

class ForExpenseAddForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'date', 'category']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        categories = kwargs.pop('categories', None)
        super(ForExpenseAddForm, self).__init__(*args, **kwargs)
        if categories:
            self.fields['category'].queryset = categories
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError('Kwota musi być większa niż zero.')
        return amount