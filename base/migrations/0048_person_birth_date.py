# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-05-19 20:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0047_auto_20160516_2107'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='birth_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='employee',
            field=models.BooleanField(default=False),
        ),
    ]
