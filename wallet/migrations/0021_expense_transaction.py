# Generated by Django 5.0 on 2024-02-18 14:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0020_alter_savings_categories'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='transaction',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='wallet.transaction'),
        ),
    ]
