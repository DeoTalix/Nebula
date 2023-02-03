# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from ..models import EmailStatus




class EmailStatusInline(admin.TabularInline):
    model = EmailStatus
    max_num = 1
    readonly_fields = [f.name for f in EmailStatus._meta.fields]

    
class EmailStatusAdmin(admin.ModelAdmin):
    model = EmailStatus
    list_display = [f.name for f in EmailStatus._meta.fields] 
    list_filter  = "person", "message", "opened"

admin.site.register(EmailStatus, EmailStatusAdmin)