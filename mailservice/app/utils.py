# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import json
import urllib2 as urllib
import urlparse

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


def get_ngrok_hostname():
    """Get ngrok random hostname if possible.

    Raises
    ------
    IOError
        Means ngrok server is not running.

    Returns
    -------
    str
    """
    r = urllib.urlopen("http://127.0.0.1:4040/api/tunnels")
    data = json.loads(r.read())
    url = urlparse.urlparse(data["tunnels"][0]["public_url"])
    return url.hostname
