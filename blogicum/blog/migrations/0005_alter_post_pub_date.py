# Generated by Django 3.2.16 on 2023-10-16 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_auto_20231016_1922'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(help_text='\n        Если установить дату и время в будущем — можно\n        делать отложенные публикации.', verbose_name='Дата и время публикации'),
        ),
    ]
