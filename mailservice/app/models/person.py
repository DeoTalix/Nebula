# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Person(models.Model):
    """Mail recepient model
    
    Attributes
    ----------
    name        : str
    email       : str
    birthday    : datetime or None, default = None

    email
        Constrained to be unique.
    """

    name = models.CharField(
        "Имя получателя", 
        max_length=200,
        blank=False, 
        null=False
    )
    email = models.EmailField(
        "Email получателя",
        unique=True,
        blank=False,
        null=False,
    )
    birthday = models.DateField(
        "День рождения получателя", 
        blank=True, 
        null=True
    )

    def __str__(self):
        return self.email

    def serialize(self):
        """Copy object field values to a dict.

        Returns
        -------
        dict[str, int | str | None]
            A dict of fields' values.
        """
        # Get field values (except foreign relations)
        result = { f.name:getattr(self, f.name) for f in self._meta.fields }

        return result