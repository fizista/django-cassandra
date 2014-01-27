# -*- encoding: utf-8 -*-
# Adding a partial compatibility code up to version Python 3.x
# http://docs.python.org/2/library/__future__.html
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys

from django.db.backends import BaseDatabaseClient

from . import CQL_VERSION


class DatabaseClient(BaseDatabaseClient):

    executable_name = 'cqlsh'

    def runshell(self):
        settings_dict = self.connection.settings_dict
        args = [self.executable_name]

        if settings_dict['USER']:
            args += ["--username", settings_dict['USER']]
        if settings_dict['PASSWORD']:
            args.extend(["--password", str(settings_dict['PASSWORD'])])
        if settings_dict['NAME']:
            args.extend(["--keyspace", str(settings_dict['NAME'])])
        if settings_dict['NAME']:
            args.extend(["--keyspace", str(settings_dict['NAME'])])
        args.extend(["--cqlversion", CQL_VERSION])

        if settings_dict['HOST']:
            args.append(settings_dict['HOST'])
        if settings_dict['PORT']:
            args.append(str(settings_dict['PORT']))

        if os.name == 'nt':
            sys.exit(os.system(" ".join(args)))
        else:
            os.execvp(self.executable_name, args)

