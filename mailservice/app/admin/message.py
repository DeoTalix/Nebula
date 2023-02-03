# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from ..models import Message
from .status import EmailStatusInline




class MessageAdmin(admin.ModelAdmin):
    model = Message
    list_display = [f.name for f in Message._meta.fields]
    list_filter = "person", "status", "due_date", "date_sent", "template"

    inlines = EmailStatusInline,

admin.site.register(Message, MessageAdmin)