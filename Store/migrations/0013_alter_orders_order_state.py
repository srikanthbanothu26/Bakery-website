# Generated by Django 5.2.3 on 2025-07-13 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0012_remove_orders_date_orders_order_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='order_state',
            field=models.CharField(choices=[('draft', 'Draft'), ('confirm', 'Confirmed'), ('cancel', 'Cancelled')], max_length=20),
        ),
    ]
