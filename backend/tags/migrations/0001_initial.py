# Generated by Django 3.2 on 2023-07-25 20:43

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Имя')),
                ('color', models.CharField(max_length=7, unique=True, validators=[django.core.validators.RegexValidator('^#([A-Fa-f0-9]{3}){1,2}$')], verbose_name='Цвет')),
                ('slug', models.SlugField(max_length=200, unique=True, verbose_name='Слаг')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
            },
        ),
    ]