# Generated by Django 5.1.2 on 2024-10-26 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_shoe_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shoe',
            name='image',
        ),
        migrations.AddField(
            model_name='shoe',
            name='image_name',
            field=models.CharField(default='default_image.png', max_length=255),
            preserve_default=False,
        ),
    ]
