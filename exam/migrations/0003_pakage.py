# Generated by Django 5.0.6 on 2024-05-28 11:57

import ckeditor.fields
import embed_video.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0002_exam_answer_correct_answer_correct_answer_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pakage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=225, null=True)),
                ('Tags', models.CharField(max_length=225, null=True)),
                ('remove_pakage', models.BooleanField(default=False, null=True)),
                ('old_price', models.IntegerField(blank=True, null=True)),
                ('price', models.IntegerField(null=True)),
                ('sku', models.CharField(blank=True, max_length=225, null=True, unique=True)),
                ('main_image', models.ImageField(blank=True, null=True, upload_to='static/images/pakage/')),
                ('on_homePage', models.BooleanField(default=False)),
                ('shor_des', ckeditor.fields.RichTextField()),
                ('des', ckeditor.fields.RichTextField()),
                ('best_selling', models.BooleanField(blank=True, null=True)),
                ('video', embed_video.fields.EmbedVideoField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
    ]
