# Generated by Django 5.1.2 on 2024-11-27 17:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0016_alter_sale_shoe_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sale',
            name='shoe_category',
        ),
        migrations.RemoveField(
            model_name='sale',
            name='shoe_image',
        ),
    ]
