# -*- encoding: utf-8 -*-
# Adding a partial compatibility code up to version Python 3.x
# http://docs.python.org/2/library/__future__.html
from __future__ import absolute_import, division, print_function, unicode_literals

from django.db import models


# Defined primary key
class DataPrimary(models.Model):
    id = models.IntegerField('ID', primary_key=True)
    data = models.IntegerField('Data')


# Automatic primary key
class DataPrimaryAuto(models.Model):
    data = models.IntegerField('Data')


# Indexing data for columns
class DataIndex(models.Model):
    id = models.IntegerField('ID', primary_key=True)
    data_index = models.IntegerField('Data index', db_index=True)
    data = models.IntegerField('Data')


# Different fields
class DataFields(models.Model):
    id = models.IntegerField('ID', primary_key=True)

    integer_field = models.IntegerField('Integer')
    datetime_field = models.DateTimeField('Date Time')
    time_field = models.TimeField('Date Time')
    date_field = models.DateField('Date')
    char_field = models.CharField('Char', max_length=200)
    text_field = models.CharField('Char', max_length=200)

