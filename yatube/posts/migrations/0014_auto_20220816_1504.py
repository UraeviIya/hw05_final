# Generated by Django 2.2.16 on 2022-08-16 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0013_post_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации'),
        ),
    ]
