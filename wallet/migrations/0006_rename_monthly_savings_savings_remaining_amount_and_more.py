# Generated by Django 5.0 on 2024-01-30 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0005_savings_monthly_savings'),
    ]

    operations = [
        migrations.RenameField(
            model_name='savings',
            old_name='monthly_savings',
            new_name='remaining_amount',
        ),
        migrations.AddField(
            model_name='savings',
            name='last_deposit_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]