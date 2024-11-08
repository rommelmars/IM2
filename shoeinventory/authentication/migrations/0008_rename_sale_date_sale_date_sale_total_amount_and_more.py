# Generated by Django 5.1.2 on 2024-10-27 02:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0007_sale'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sale',
            old_name='sale_date',
            new_name='date',
        ),
        migrations.AddField(
            model_name='sale',
            name='total_amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.00018298931342409602, max_digits=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='sale',
            name='shoe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.shoe'),
        ),
    ]
