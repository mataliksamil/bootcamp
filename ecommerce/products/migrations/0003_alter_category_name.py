# Generated by Django 3.2.9 on 2021-12-04 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_auto_20211204_1153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=255, verbose_name='CategoryName'),
        ),
    ]
