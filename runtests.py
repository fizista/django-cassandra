#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import sys
import os
from os.path import join, realpath, dirname

_DIR_ = realpath(dirname(__file__))

os.chdir(_DIR_)
sys.path.insert(0, realpath(_DIR_))

from project import settings as settings_base
from django.conf import settings

settings.configure(
    default_settings=settings_base,
    DEBUG=False,
)

from django.test.simple import DjangoTestSuiteRunner
test_runner = DjangoTestSuiteRunner(verbosity=1)

failures = test_runner.run_tests(['data', ])
if failures:
    sys.exit(failures)

