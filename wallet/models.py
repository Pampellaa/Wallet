from datetime import date

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()

    def __str__(self):
        return self.name


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    date = models.DateField()
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)

    # currency = models.ForeignKey('Currency', on_delete=models.CASCADE, null=True, blank=True)
    def transaction_type(self):
        return 'Expense'


class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    date = models.DateField()
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)

    # currency = models.ForeignKey('Currency', on_delete=models.CASCADE)
    def transaction_type(self):
        return 'Income'


class Savings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    goal_amount = models.DecimalField(max_digits=100, decimal_places=2)
    current_amount = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    categories = models.ManyToManyField(Category, blank=True, null=True)
    remaining_amount = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    last_deposit_date = models.DateField(null=True, blank=True)

    @property
    def today(self):
        return date.today()

    @property
    def monthly_deposit(self):
        months = relativedelta(self.end_date, self.today).months
        if months == 0:
            return self.goal_amount
        else:
            return self.remaining_amount / months

    def save(self, *args, **kwargs):
        self.remaining_amount = self.goal_amount - self.current_amount
        self.last_deposit_date = timezone.now().date()
        super().save(*args, **kwargs)


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=64)
    symbol = models.CharField(max_length=5, blank=True, null=True)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.code


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=100, decimal_places=2, default=0.0)


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('Expense', 'Expense'),
        ('Income', 'Income'),
        ('Savings', 'Savings'),
        ('Exchange', 'Exchange')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    transaction_type = models.CharField(max_length=8, choices=TRANSACTION_TYPES)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, default=153)
