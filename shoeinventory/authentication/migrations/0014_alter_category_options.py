# Generated by Django 5.1.2 on 2024-11-22 16:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0013_category_shoe_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'Categories'},
        ),
    ]
