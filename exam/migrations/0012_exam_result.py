# Generated by Django 5.0.6 on 2024-05-28 23:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0011_exam_order_exam_pakage_alter_exam_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='result',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
