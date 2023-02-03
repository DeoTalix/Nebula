import os
import logging

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .models import (
    Person,
    Message,
    EmailStatus,
)
from .utils import render_content_template
from mailservice.celery import app


log = logging.getLogger("django")


@app.task
def on_success(self, retval, task_id, args, kwargs):
    """Success handler for message sending task. Adds success data to report 
    field of EmailStatus object.

    Parameters
    ----------
    retval  : int
    task_id : int
    args    : tuple[int | str | bool | list[str] | None]
    kwargs  : dict[str, Any]

    Returns
    -------
    None
    """
    message_id, person_id = args[0], args[1]
    status, _ = EmailStatus.objects.get_or_create(
        message__id=message_id, 
        person__id=person_id
    )
    status.add_record("Successful transaction on %s" % timezone.now())


@app.task
def on_failure(self, exc, task_id, args, kwargs, einfo):
    """Failure handler for message sending task. Adds failure data to report 
    field of EmailStatus object.

    Parameters
    ----------
    exc     : Exception
    task_id : int
    args    : tuple[int | str | bool | list[str] | None]
    kwargs  : dict[str, Any]
    einfo   : ExceptionInfo

    Returns
    -------
    None
    """
    message_id, person_id = args[0], args[1]
    status, _ = EmailStatus.objects.get_or_create(
        message__id=message_id, 
        person__id=person_id
    )
    status.add_record("Failed transaction on %s" % timezone.now())


@app.task(
    soft_time_limit=settings.BROADCAST_MAX_TIMEOUT,
    link=on_success.s(), 
    link_error=on_failure.s())
def send_message(mail_id, person_id, *args, **kwargs):
    """Async wrapper for django.core.mail.send_mail.

    Parameters
    ----------
    mail_id   : int
    person_id : int

    Returns
    -------
    None
    """
    return send_mail(*args, **kwargs)


def render_message(message, person, template):
    """Render email with user provided text and template.

    Parameters
    ----------
    message  : app.models.Message
    person   : app.models.Person
    template : str
        Template html string loaded from mail template directory.

    Returns
    -------
    str 
    """
    # Render user provided content with person info as context parameter
    rendered_content = render_content_template(
        message.text,
        dict(
            username = person.name,
            birthday = person.birthday,
            email    = person.email,
        ),
    )
    # Render mail template with rendered user content as {{ content }}.
    # person_id and mail_id are rendered to the tracker url to be identified 
    # later. Example: /tracker-endpoint/{person_id}-{mail_id}/logo.png
    rendered_message = render_content_template(
        template,
        dict(
            person_id = person.id,
            mail_id   = message.id,
            content   = rendered_content,
            current_host = settings.CURRENT_HOST,
            current_port = settings.CURRENT_PORT,
        ),
    )
    return rendered_message


def broadcast_message(message):
    """Render message with each person's context and send it. Update message 
    status.

    Parameters
    ----------
    message: app.models.Message

    Returns
    -------
    None
    """

    # Get absolute path to template
    path = os.path.join(settings.TEMPLATES_MAIL_PATH, message.template)
    try:
        # Read template
        with open(path, "r") as file:
            mail_template_text = file.read()
    except Exception as e:
        log.exception(e)
        return

    persons = message.person.all()

    # Set message status to "busy" in order to prevent broadcast beat from 
    # processing it
    message.status = "b"
    message.save()

    # Iteration over each person is necessary in order to be able to render
    # provided content and template with persons data context
    for person in persons:
        try:
            rendered_message = render_message(
                message, 
                person, 
                mail_template_text
            )
        except Exception as e:
            log.exception(e)
            continue
        
        # Send message to a person asynchronously
        args = (
            message.id,
            person.id,
            message.subject,
            rendered_message,
            settings.EMAIL_HOST_USER,
            (person.email,),
        )
        kwargs = dict(
            html_message = rendered_message,
            fail_silently = False
        )
        task = send_message.apply_async(args, kwargs)

    # Update message status as sent
    message.status    = "s"
    message.due_date  = None
    message.date_sent = timezone.now()
    message.save()
    return


@app.task
def broadcast_message_beat():
    """Send messages that are scheduled be sent. The beat interval is set in the 
    settings CELERY_BEAT_SCHEDULE.
    """
    # Select messages with "waiting" status and a due date less than now
    messages = Message.objects.filter(status="w", due_date__lt=timezone.now())
    for message in messages:
        broadcast_message(message)


@app.task
def update_email_status(mail_id, person_id,):
    """Update email status on tracking image request.

    Parameters
    ----------
    mail_id   : int
    person_id : int

    Returns
    -------
    None
    """
    
    status = None

    try:
        # Use person and mail ids to update tracking status
        status = EmailStatus.objects.get(person=person_id, message=mail_id)
    except EmailStatus.DoesNotExist as e:
        # Try to create new status in case person and message exist
        try:
            status = EmailStatus.create_by_id(mail_id, person_id)
        except (Person.DoesNotExist, Message.DoesNotExist) as e:
            log.error(e)

    if status is None:
        return
    # Update status
    status.opened = True
    status.report += "Opened on %s\n" % timezone.now()
    status.save()
