# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from .person import Person



class Message(models.Model):
    """Email message model

    Attributes
    ----------
    person
    due_date  : date or None , default = None
    subject   : str          , default = ""
    text      : str          , default = ""
    template  : str          , default = "default-mail.html"
    status    : str          , default = "w"
    date_sent : date or None , default = None

    person
        Many to many relation for the Person model
    subject
        Mail subject
    text
        Mail plain text, intended to render with django template engine.
    template
        Name for selected template located in app/templates/mail_templates dir.
    status
        One of these statuses s, b, w, x (sent, busy, waits, canceled). 
    """
    
    person = models.ManyToManyField(
        verbose_name="Получатели",
        to=Person,
        default=1,
        blank=False,
    )
    due_date = models.DateTimeField(
        "Дата будущего отправления",
        blank=True,
        null=True,
    )
    subject = models.CharField(
        "Тема сообщения",
        max_length=200,
        default="",
        blank=False,
        null=False,
    )
    text = models.TextField(
        "Текст сообщения",
        default="",
        blank=True,
        null=False,
    )
    template = models.CharField(
        "Путь к файлу шаблона",
        max_length=200,
        default="default-mail.html",
        blank=False,
        null=False,
    )
    status = models.CharField(
        "Статус сообщения",
        max_length=1,
        choices=[
            ("w", "Ожидает отправки"),
            ("b", "В работе"),
            ("s", "Отправлено"),
            ("x", "Отменено"),
        ],
        default="w",
        blank=False,
        null=False,
    )
    date_sent = models.DateTimeField(
        "Дата совершенного отправления",
        blank=True,
        null=True,
    )

    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, str(self.id))

    def serialize(self):
        """Copy object field values to a dict.

        Returns
        -------
        dict[str, int | str | list[int] | None]
            A dict of field values.
        """
        # Get field values (except foreign relations)
        result = { f.name:getattr(self, f.name) for f in self._meta.fields }
        # Get many_to_many ids
        for mtm in self._meta.local_many_to_many:
            result[mtm.name] = [o.id for o in getattr(self, mtm.name)]

        return result
