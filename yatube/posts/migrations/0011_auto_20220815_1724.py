# Generated by Django 2.2.16 on 2022-08-15 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_auto_20220726_1745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(help_text='Это обязательное поле для заполнения', verbose_name='Текст поста'),
        ),
    ]
