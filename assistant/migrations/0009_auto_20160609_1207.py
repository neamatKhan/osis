# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-06-09 10:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistant', '0008_auto_20160607_1143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reviewer',
            name='role',
            field=models.CharField(choices=[('PHD_SUPERVISOR', 'phd_supervisor'), ('SUPERVISION', 'supervision'), ('RESEARCH', 'research'), ('SECTOR_VICE_RECTOR', 'sector_vice_rector')], max_length=20),
        ),
    ]
