# Generated by Django 4.2.10 on 2024-02-21 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0025_alter_currency_exchange_rate_alter_expense_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currency',
            name='exchange_rate',
            field=models.DecimalField(decimal_places=6, max_digits=10),
        ),
    ]
