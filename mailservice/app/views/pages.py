from django.shortcuts import redirect


def view_home(req, *args, **kwargs):
    return redirect("/admin/app/person")