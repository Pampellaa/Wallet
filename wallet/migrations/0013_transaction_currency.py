# Generated by Django 5.0 on 2024-01-31 18:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0012_alter_currency_exchange_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='currency',
            field=models.ForeignKey(default=5, on_delete=django.db.models.deletion.CASCADE, to='wallet.currency'),
        ),
    ]
