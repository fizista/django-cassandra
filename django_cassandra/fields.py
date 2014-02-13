# -*- encoding: utf-8 -*-
# Adding a partial compatibility code up to version Python 3.x
# http://docs.python.org/2/library/__future__.html
from __future__ import absolute_import, division, print_function, unicode_literals

import time_uuid

from django.db.models import DateTimeField
from django.utils.translation import ugettext_lazy as _


class TimeUUIDField(DateTimeField):
    """
    TimeUUIDField(auto=False)
    
    Attr:
        auto - automatically generated field, dafault: False
    
    """

    description = _("Time UUID")

    def __init__(self, verbose_name=None, name=None, auto=False, **kwargs):
        self.auto = auto
        super(TimeUUIDField, self).__init__(verbose_name, name, auto_now=auto, **kwargs)

    def get_internal_type(self):
        return "TimeUUIDField"

    def to_python(self, value):
        """
        Args:
            value - <datetime.datetime() ...> or <datetime.date() ...> or 
                    (str, bytes, unicode) with UUID string or None or <uuid.UUID() ...>  
        """

        if value is None:
            return value

        if isinstance(value, time_uuid.TimeUUID):
            return value

        if isinstance(value, (bytes, str, unicode)):
            try:
                return time_uuid.TimeUUID(value)
            except ValueError:
                pass

        return time_uuid.TimeUUID.convert(value)

    def get_prep_value(self, value):
        value = self.to_python(value)
        return value

    def get_db_prep_value(self, value, connection, prepared=False):
        if not prepared:
            value = self.get_prep_value(value)
        return value

    def value_to_string(self, obj):
        val = self._get_val_from_obj(obj)
        return '' if val is None else str(val.get_datetime())

