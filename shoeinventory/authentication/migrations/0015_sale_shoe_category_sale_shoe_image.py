# Generated by Django 5.1.2 on 2024-11-27 17:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0014_alter_category_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='shoe_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='authentication.category'),
        ),
        migrations.AddField(
            model_name='sale',
            name='shoe_image',
            field=models.ImageField(blank=True, null=True, upload_to='shoes/'),
        ),
    ]
