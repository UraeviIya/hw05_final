# Generated by Django 2.2.16 on 2022-08-16 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0014_auto_20220816_1504'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='image',
            field=models.ImageField(blank=True, upload_to='posts/', verbose_name='Картинка'),
        ),
    ]
