# Generated by Django 5.2.3 on 2025-07-05 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0003_showcaseimages'),
    ]

    operations = [
        migrations.AddField(
            model_name='showcaseimages',
            name='name',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='showcaseimages',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='static/images/showcase_images'),
        ),
    ]
