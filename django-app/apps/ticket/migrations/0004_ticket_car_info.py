# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-09 07:55
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0003_ticket_upload_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='car_info',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=None),
        ),
    ]
