# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-05-21 11:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Map', '0009_dataelement_relation'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataelement',
            name='gbif_reference',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
