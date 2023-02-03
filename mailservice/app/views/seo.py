# -*- coding: utf-8 -*-
"""Views for seo related purposes like tracking email status."""
from __future__ import unicode_literals
import os
import logging

from django.conf import settings
from django.http import HttpResponse

from ..tasks import update_email_status


log = logging.getLogger("django")

# Load image file for tracking
image_path = os.path.join(settings.BASE_DIR, "app", "static", "logo.png")
with open(image_path, "rb") as file:
    image = file.read()

response_forbidden = HttpResponse("", status=400)

def view_tracking_image(req, mail_id, person_id, *args, **kwargs):
    """View for tracking whether a person opened email or not. 
    Updates database tracker object for provided person and email id.

    Parameters
    ----------
    req         : django.http.request.HttpRequest
    person_id   : int
    mail_id     : int

    req
        Expected: get request with person and mail id.
            /tracker-endpoint/{person_id}-{mail_id}/logo.png
    person_id
        Id of a database person object that recieved the mail.
    mail_id
        Id of a database mail object that was sent to a person.

    Returns
    -------
    django.http.response.HttpResponse
        Image of logo.png if request method is of "GET" type. 
        Otherwise status 400 forbidden response.
    """
    if req.method == "GET":
        # Update email status asynchronously
        update_email_status.apply_async([mail_id, person_id,])
        # Return image response
        return HttpResponse(image, content_type="image/png")
    return response_forbidden