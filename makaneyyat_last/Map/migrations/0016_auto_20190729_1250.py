# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-07-29 12:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Map', '0015_dataelement_ar_coverage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='makaneyya',
            name='gbifQuery',
            field=models.CharField(blank=True, default='', max_length=15000),
        ),
    ]
