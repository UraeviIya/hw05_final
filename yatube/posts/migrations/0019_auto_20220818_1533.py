# Generated by Django 2.2.16 on 2022-08-18 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0018_auto_20220817_1117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата публикации'),
        ),
    ]
