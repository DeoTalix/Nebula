# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import json
import urllib2 as urllib
import urlparse
from time import sleep

from django.template import (
    Template, 
    Context
)


def render_content_template(content, ctx):
    """Render user provided content with a given context to a string using
    django template engine.

    Parameters
    ----------
    content : str
    ctx     : dict[str, str | None]
        Expected dictionary:
            {
                "username" : "User Name",
                "birthday" : "2023-01-01",
            }

    Returns
    -------
    str
    """
    context = Context(ctx)
    content_template = Template(content)
    rendered_content = content_template.render(context)
    return rendered_content


def get_ngrok_host(number_of_tries=3, sleep_timeout=1):
    """Get ngrok random hostname if possible.

    Parameters
    ----------
    number_of_tries : int, default=3
    sleep_timeout   : int, default=1

    Returns
    -------
    tuple[str, str] | None
        A tuple of ngrok hostname and "" for the port or None.
    """
    from django.conf import settings
    
    url = settings.NGROK_TUNNELS_URL
    for _ in range(number_of_tries):
        try:
            r = urllib.urlopen(url)
            data = json.loads(r.read())
            url = urlparse.urlparse(data["tunnels"][0]["public_url"])
            return (url.hostname, "")
        except Exception as e:
            sleep(sleep_timeout)
