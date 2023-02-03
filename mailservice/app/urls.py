from django.conf.urls import url

from .views import (
    view_tracking_image,
    ajax_email_preview,
    ajax_new_message_form_submit,
    ajax_get_mail_template_list
)

urlpatterns = [
    url(
        r"^media-files/(?P<mail_id>\d+)-(?P<person_id>\d+)/logo.png$", 
        view_tracking_image, 
        name="tracking-image"
    ),
    url(
        r"^email-preview$", 
        ajax_email_preview, 
        name="ajax-email-preview"
    ),
    url(
        r"^forms/new-message-form$", 
        ajax_new_message_form_submit, 
        name="ajax-new-message-form"
    ),
    url(
        r"^forms/get-mail-template-list$", 
        ajax_get_mail_template_list, 
        name="ajax-get-mail-template-list"
    ),
]
