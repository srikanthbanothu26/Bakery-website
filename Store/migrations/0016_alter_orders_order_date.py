# Generated by Django 5.2.3 on 2025-07-13 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0015_alter_orders_order_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='order_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
