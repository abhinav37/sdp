# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-20 16:23
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_auto_20161120_1620'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='component',
            name='filetype',
        ),
    ]