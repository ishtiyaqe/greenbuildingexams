# Generated by Django 5.0.6 on 2024-05-30 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0019_affiliate_earning_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='exam',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]