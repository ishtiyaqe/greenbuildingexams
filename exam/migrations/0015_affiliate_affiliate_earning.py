# Generated by Django 5.0.6 on 2024-05-29 22:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0014_alter_answer_answer_alter_answer_question_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='affiliate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('affiliate_code', models.CharField(max_length=255)),
                ('total_amunt', models.CharField(max_length=255)),
                ('paypal_address', models.CharField(max_length=255)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='affiliate_earning',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_amunt', models.CharField(max_length=255)),
                ('comision_amunt', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('affiliate_account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='exam.affiliate')),
                ('order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='exam.order')),
            ],
        ),
    ]
