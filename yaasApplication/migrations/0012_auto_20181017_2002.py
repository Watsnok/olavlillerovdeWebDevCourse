# Generated by Django 2.1.1 on 2018-10-17 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yaasApplication', '0011_auto_20181017_1959'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='minprice',
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
    ]
