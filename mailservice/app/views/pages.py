from django.shortcuts import redirect
from django.conf import settings


def view_home(req, *args, **kwargs):
    if settings.NGROK is True:
        return redirect("https://" + settings.CURRENT_HOST + "/admin/app/person")
    return redirect("/admin/app/person")