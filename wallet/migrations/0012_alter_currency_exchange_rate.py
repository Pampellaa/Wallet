# Generated by Django 5.0 on 2024-01-31 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0011_alter_currency_exchange_rate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currency',
            name='exchange_rate',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
