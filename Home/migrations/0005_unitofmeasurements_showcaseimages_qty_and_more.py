# Generated by Django 5.2.3 on 2025-07-05 13:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0004_showcaseimages_name_alter_showcaseimages_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnitOfMeasurements',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='showcaseimages',
            name='qty',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='showcaseimages',
            name='weight',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='showcaseimages',
            name='uom',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Home.unitofmeasurements'),
        ),
    ]
