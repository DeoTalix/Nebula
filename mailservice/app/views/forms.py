# -*- coding: utf-8 -*-
"""Views for ajax post requests."""
from __future__ import unicode_literals
import json
import os
from datetime import date

from django.http.response import (
    HttpResponse, 
    JsonResponse
)
from django.shortcuts import render
from django.conf import settings

from ..models import (
    Message,
    Person,
)
from ..tasks import broadcast_message
from ..utils import render_content_template




response_forbidden = HttpResponse("", status = 400)

def ajax_new_message_form_submit(req, *args, **kwargs):
    """Post request view for "new message form" submition endpoint.

    Parameters
    ----------
    req : django.http.request.HttpRequest
        Expected: post method request with json object containg new message form 
        data and person ids. 
            {
                "form_data" : {
                    "due_date": "2023-01-01T00:00",
                    "subject" : "Message subject",
                    "message" : "Message text", 
                    "template": "default-mail.html"
                },
                "person_ids": [1, 2, 3]
            }

    Returns
    -------
    django.http.response.HttpResponse
        "OK" and status 200 if no errors occurred.
        Status 400 if request method is not "POST"
        Status 500 if errors occurred.
    """
    if req.method == "POST":
        # Parse form data
        data = json.load(req)
        # Create new message object using form data
        form_data = data.get("form_data")
        message = Message.objects.create(
            due_date = form_data.get("due_date") or None,
            subject  = form_data.get("subject"),
            text     = form_data.get("message"),
            template = form_data.get("template"),
        )
        # Get person queryset
        person_ids = data.get("person_ids")
        persons = Person.objects.filter(id__in=person_ids)
        # Attach person queryset to message and save again
        message.person = persons
        message.save()
        # Send non blocking messages immediately to each recepient
        # if due date is not set
        if message.due_date is None:
            broadcast_message(message)
        else:
            pass
        # Return confirmation status
        return HttpResponse("OK")
    return response_forbidden


def ajax_get_mail_template_list(req, *args, **kwargs):
    """Post request view for "mail temlate list" request.

    Parameters
    ----------
    req : django.http.request.HttpRequest
        Expected: post method request with empty json object.

    Returns
    -------
    django.http.response.JsonResponse or django.http.response.HttpResponse
        A list of mail template names from /app/templates/mail_templates dir
        and status 200 if no errors occurred.
        Status 400 if request method is not "POST"
        Status 500 if errors occurred.
    """
    if req.method == "POST":
        # Get a list of template names from settings path
        templates = os.listdir(settings.TEMPLATES_MAIL_PATH)
        # Return them as json
        data = json.dumps(templates)
        return JsonResponse(data, safe=False)
    return response_forbidden


def ajax_email_preview(req, *args, **kwargs):
    """Post request view for "mail temlate preview" request.

    Parameters
    ----------
    req : django.http.request.HttpRequest
        Expected: post method request with json object containing form data.
            {
                "message" : "Message text", 
                "template": "default-mail.html"
            }

    Returns
    -------
    django.http.response.HttpResponse
        A rendered mail template with dummy context parameters and status 200 
        if no errors occurred.
        Status 400 if request method is not "POST"
        Status 500 if errors occurred.
    """
    if req.method == "POST":
        # Parse json data
        data = json.load(req)
        message = data.get("message")
        template = data.get("template")
        # Return status 500 if no template found in json data
        if template is None:
            return HttpResponse("", status = 500)  
        # Create dummy context for template preview
        dummy_context = dict(
            username = 'Имя пользователья',
            birthday = date.today(),
        )
        # Render message provided by user
        rendered_message = render_content_template(message, dummy_context)
        # Create new context for mail template that wraps rendered user message
        context = dict(
            content = rendered_message,
            person_id=1,
            mail_id=1,
        )
        # Get mail template dir from setting path
        # Conctenate it with template name
        mail_template_dirname = os.path.split(settings.TEMPLATES_MAIL_PATH)[-1]
        template_name = mail_template_dirname + "/%s" % template
        # Return rendered template
        return render(req, template_name, context)
    return response_forbidden