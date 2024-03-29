# Generated by Django 5.0 on 2024-02-02 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0017_alter_expense_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='is_built',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='savings',
            name='categories',
            field=models.ManyToManyField(blank=True, null=True, to='wallet.category'),
        ),
    ]
