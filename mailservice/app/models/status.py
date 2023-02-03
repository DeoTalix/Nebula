# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime

from django.db import models
from django.utils import timezone

from .person import Person
from .message import Message


class EmailStatus(models.Model):
    """Отчет об отправке сообщения
    
    Attributes
    ----------
    person  : app.models.Person
    message : app.models.Message
    opened  : bool
    report  : str
        Report contains various messages about email state. 
        In case of failure error message will be stored in this field.
    """
    person = models.ForeignKey(
        Person, 
        verbose_name="Получатель", 
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )
    message = models.ForeignKey(
        Message, 
        verbose_name="Сообщение", 
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )
    opened = models.BooleanField(
        "Письмо было открыто",
        default=False,
        blank=False,
        null=False
    )
    report = models.TextField(
        "Отчет",
        default="",
        blank=False,
        null=False
    )

    def add_record(self, text):
        """A method for appending text to report.

        Parameters
        ----------
        text : str

        Returns
        -------
        None
        """
        self.report += text + '\n'
        self.save()

    @classmethod
    def create_by_id(cls, message_id, person_id):
        """A class method for creating EmailStatus instance with provided 
        arguments.
        
        Parameters
        ----------
        message_id : int
        person_id  : int

        Raises
        ------
        Message.DoesNotExist
        Person.DoesNotExist

        Returns
        -------
        app.models.EmailStatus
        """
        message = Message.objects.get(id=message_id)
        person  = Person.objects.get(id=person_id)
        status  = cls.objects.create(
            person  = person,
            message = message,
        )
        status.add_record("Created on %s" % timezone.now())
        return status

    # @classmethod
    # def get_or_create(cls, message_id, person_id):
    #     """A class method for getting or otherwise creating new EmailStatus
    #     instance.

    #     Parameters
    #     ----------
    #     message_id : int
    #     person_id  : int

    #     Returns
    #     -------
    #     app.models.EmailStatus
    #     """
    #     try:
    #         return cls.objects.get(message__id=message_id, person__id=person_id)
    #     except EmailStatus.DoesNotExist:
    #         return cls.create_by_id(message_id, person_id)