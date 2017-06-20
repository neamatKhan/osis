# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-05-04 07:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0111_offertype'),
    ]

    operations = [
        migrations.AddField(
            model_name='offeryear',
            name='offer_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.OfferType'),
        ),
    ]