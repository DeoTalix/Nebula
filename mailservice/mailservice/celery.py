# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import logging

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mailservice.settings")

app = Celery('mailservice')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()