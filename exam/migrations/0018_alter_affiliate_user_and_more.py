# Generated by Django 5.0.6 on 2024-05-30 12:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0017_alter_affiliate_total_order'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='affiliate',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='affiliate_earning',
            name='affiliate_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.affiliate'),
        ),
    ]
