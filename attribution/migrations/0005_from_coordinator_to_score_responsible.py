# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-05 09:13
from __future__ import unicode_literals
from django.db import migrations
from django.db import connection
from django.db import transaction


@transaction.atomic
def set_coordinators_as_score_responsible(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute("""UPDATE attribution_attribution SET score_responsible = TRUE
                          WHERE function = 'COORDINATOR';""")


class Migration(migrations.Migration):

    dependencies = [
        ('attribution', '0004_attribution_score_responsible'),
    ]

    operations = [
        migrations.RunPython(set_coordinators_as_score_responsible),
    ]