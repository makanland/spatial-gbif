# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-06-20 10:53
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='dci',
            fields=[
                ('id', models.AutoField(max_length=500, primary_key=True, serialize=False, verbose_name='id')),
                ('Title', models.CharField(blank=True, max_length=500, null=True, verbose_name='Title')),
                ('Creator', models.CharField(blank=True, max_length=500, null=True)),
                ('Subject', models.CharField(blank=True, max_length=500, null=True)),
                ('Description', models.CharField(blank=True, max_length=500, null=True)),
                ('Publisher', models.CharField(blank=True, max_length=500, null=True)),
                ('Contributor', models.CharField(blank=True, max_length=500, null=True)),
                ('Date', models.DateField(blank=True, null=True)),
                ('Type', models.CharField(blank=True, max_length=500, null=True)),
                ('Format', models.CharField(blank=True, max_length=500, null=True)),
                ('Source', models.CharField(blank=True, max_length=500, null=True)),
                ('Language', models.CharField(blank=True, max_length=500, null=True, verbose_name='')),
                ('Relation', models.CharField(blank=True, max_length=500, null=True)),
                ('Coverage', models.CharField(blank=True, max_length=500, null=True)),
                ('ar_Title', models.CharField(blank=True, max_length=50, null=True, verbose_name='Arabic Title')),
                ('ar_Creator', models.CharField(blank=True, max_length=500, null=True)),
                ('ar_Subject', models.CharField(blank=True, max_length=500, null=True)),
                ('ar_Description', models.CharField(blank=True, max_length=50, null=True)),
                ('ar_Publisher', models.CharField(blank=True, max_length=500, null=True)),
                ('ar_Contributor', models.CharField(blank=True, max_length=500, null=True)),
                ('ar_Type', models.CharField(blank=True, max_length=500, null=True)),
                ('ar_Format', models.CharField(blank=True, max_length=500, null=True)),
                ('Identifier', models.FileField(blank=True, null=True, upload_to='uploads/%Y/%m/%d/')),
                ('ar_Source', models.CharField(blank=True, max_length=500, null=True)),
                ('ar_Language', models.CharField(blank=True, max_length=2, null=True, verbose_name='')),
                ('ar_Relation', models.CharField(blank=True, max_length=500, null=True)),
                ('ar_Coverage', models.CharField(blank=True, max_length=50, null=True)),
                ('ar_rights', models.CharField(blank=True, max_length=500, null=True)),
                ('rights', models.CharField(blank=True, max_length=500, null=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('geo_referenced', models.BooleanField(default=False)),
                ('lon', models.FloatField(blank=True, default=1.0, null=True, verbose_name='longitude')),
                ('lat', models.FloatField(blank=True, default=1.0, null=True, verbose_name='latitude')),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
                ('properties', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
        ),
    ]
