# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from ..models import Person
from .status import EmailStatusInline




class PersonAdmin(admin.ModelAdmin):
    model = Person
    list_display = [f.name for f in Person._meta.fields]
    list_filter = "birthday",
    change_list_template = "admin/app/persons_change_list.html"

    inlines = EmailStatusInline,

admin.site.register(Person, PersonAdmin)