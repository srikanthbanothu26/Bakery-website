# Generated by Django 5.2.3 on 2025-07-13 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0010_orders_date_orders_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='order_state',
            field=models.CharField(choices=[('draft', 'Draft'), ('confirm', 'Confirmed'), ('cancel', 'Cancelled')], default='draft', max_length=20),
        ),
    ]
