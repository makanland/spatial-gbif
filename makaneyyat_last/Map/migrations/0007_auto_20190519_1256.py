# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-05-19 12:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Map', '0006_auto_20190519_1255'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataelement',
            name='format',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
