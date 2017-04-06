# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-04-05 07:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from osis_common.models.serializable_model import SerializableModel
from internship.models.cohort import Cohort
from internship.models.internship import Internship
import uuid

def buildNeededInternships(apps, schema_editor):
    InternshipChoice = apps.get_model("internship", "InternshipChoice")
    db_alias = schema_editor.connection.alias
    default_cohort = Cohort.objects.first()
    existing_choices_values = InternshipChoice.objects.values_list("internship_choice", flat=True)
    internship_ids_to_create   = sorted(list(set(existing_choices_values)))
    for internship_id in internship_ids_to_create:
        internship = Internship(id=internship_id, name="Au choix {id}".format(id=internship_id), cohort=default_cohort)
        super(SerializableModel, internship).save()

class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0038_optimize_organization_address_queries'),
    ]

    operations = [
        migrations.CreateModel(
            name='Internship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('length_in_periods', models.IntegerField(default=1)),
                ('cohort', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='internship.Cohort')),
                ('speciality', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='internship.InternshipSpeciality')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RunPython(buildNeededInternships)
    ]
