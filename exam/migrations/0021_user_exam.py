# Generated by Django 5.0.6 on 2024-06-01 19:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0020_alter_exam_end_time_alter_exam_start_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='User_exam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=800, null=True)),
                ('answer', models.CharField(max_length=800)),
                ('correct_answer', models.CharField(max_length=800)),
                ('is_correct', models.BooleanField(default=False)),
                ('exam', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='exam.exam')),
            ],
        ),
    ]