# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-05-04 12:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0002_internshipchoice'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('changed', models.DateTimeField(null=True)),
                ('name', models.CharField(max_length=255)),
                ('acronym', models.CharField(max_length=15)),
                ('website', models.URLField(blank=True, max_length=255, null=True)),
                ('reference', models.CharField(blank=True, max_length=30, null=True)),
                ('type', models.CharField(blank=True, max_length=30, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrganizationAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=20)),
                ('location', models.CharField(max_length=255)),
                ('postal_code', models.CharField(max_length=20)),
                ('city', models.CharField(max_length=255)),
                ('country', models.CharField(max_length=255)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='internship.Organization')),
            ],
        ),
    ]
