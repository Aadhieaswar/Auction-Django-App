# Generated by Django 3.0.7 on 2020-11-02 00:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_auto_20201102_0012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='added',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
