# Generated by Django 5.0.6 on 2024-05-28 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0003_pakage'),
    ]

    operations = [
        migrations.AddField(
            model_name='pakage',
            name='pdf',
            field=models.FileField(blank=True, null=True, upload_to='static/pdfs/pakage/'),
        ),
    ]
