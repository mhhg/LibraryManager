# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('serial', models.BigIntegerField(unique=True)),
                ('no', models.PositiveSmallIntegerField(default=1)),
                ('price', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('buyer_first_name', models.CharField(max_length=100)),
                ('buyer_last_name', models.CharField(max_length=100)),
                ('seller', models.PositiveSmallIntegerField(default=3, choices=[(1, b'Kashani'), (2, b'Hojabri'), (3, b'Other')])),
                ('date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('no', models.PositiveSmallIntegerField(default=1)),
                ('book', models.ForeignKey(to='manager.Book')),
                ('invoice', models.ForeignKey(to='manager.Invoice')),
            ],
        ),
        migrations.AddField(
            model_name='invoice',
            name='books',
            field=models.ManyToManyField(to='manager.Book', through='manager.InvoiceItem'),
        ),
    ]
