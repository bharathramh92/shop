# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-16 03:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store_db', '0005_remove_inventory_available_countries'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inventory',
            name='domestic_shipping_company',
        ),
        migrations.RemoveField(
            model_name='inventory',
            name='domestic_shipping_cost',
        ),
    ]
