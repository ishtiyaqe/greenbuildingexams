# Generated by Django 4.0.8 on 2022-12-01 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_customuser_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='phone',
            field=models.CharField(help_text='Enter 11 digits phone number', max_length=11, unique=True, verbose_name='Phone Number'),
        ),
    ]
