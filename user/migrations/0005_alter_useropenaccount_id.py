# Generated by Django 5.1.1 on 2025-04-13 19:02

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_useractivitylog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useropenaccount',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
