# -*- coding:Utf-8 -*-

from celery.task import task, periodic_task
from celery.schedules import crontab

from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, get_connection
from django.utils.timezone import make_aware, utc
from django.template import Context
from datetime import datetime, date, time, timedelta

from bson import DBRef, ObjectId

from vosae_utils import respect_language


@task()
def update_calendar_ical_data(calendar):
    calendar.reload()
    calendar.ical_data = calendar.to_ical()
    calendar.save()


@periodic_task(run_every=crontab(minute=0, hour=0))
def schedule_reminders():
    from organizer.models import VosaeEvent
    start = make_aware(datetime.combine(date.today(), time()), utc)
    end = start + timedelta(1)
    for vosae_event in VosaeEvent.objects.filter(next_reminder__at__gte=start, next_reminder__at__lt=end):
        emit_reminders.apply_async(eta=vosae_event.next_reminder.at, kwargs={'vosae_event_id': unicode(vosae_event.id)})


@task()
def emit_reminders(vosae_event_id):
    from organizer.models import CalendarList, VosaeEvent
    from notification import models as notifications
    try:
        vosae_event = VosaeEvent.objects.get(id=vosae_event_id)
    except:
        # Event retrieval failed (maybe deleted in the meantime)
        return None
    calendar_lists = CalendarList.objects.filter(calendar=vosae_event.calendar)

    reminders = {
        'EMAIL': {},
        'POPUP': set([])
    }
    # Event reminders
    for method in set([reminder.method for reminder in vosae_event.reminders.overrides if reminder.minutes == vosae_event.next_reminder.threshold]):
        if method == 'EMAIL':
            vosae_users = [calendar_list.vosae_user for calendar_list in calendar_lists]
            for vosae_user in vosae_users:
                user_lang = vosae_user.get_language()
                if not user_lang in reminders['EMAIL']:
                    reminders['EMAIL'][user_lang] = set([])
                reminders['EMAIL'][user_lang].update([vosae_user.email])
        elif method == 'POPUP':
            reminders['POPUP'].update([unicode(calendar_list.vosae_user.id) for calendar_list in calendar_lists])

    # Default reminders
    if vosae_event.reminders.use_default:
        for calendar_list in calendar_lists:
            for method in set([reminder.method for reminder in calendar_list.reminders if reminder.minutes == vosae_event.next_reminder.threshold]):
                if method == 'EMAIL':
                    user_lang = calendar_list.vosae_user.get_language()
                    if not user_lang in reminders['EMAIL']:
                        reminders['EMAIL'][user_lang] = set([])
                    reminders['EMAIL'][user_lang].update([calendar_list.vosae_user.email])
                elif method == 'POPUP':
                    reminders['POPUP'].update([unicode(calendar_list.vosae_user.id)])

    # Prefill context
    timezone = vosae_event.get_start_timezone()
    start = vosae_event._get_next_occurrence(after=vosae_event.next_reminder.at).astimezone(timezone)
    context = {
        'vosae_event': vosae_event,
        'start': start.replace(tzinfo=None),
        'timezone': start.tzname(),
        'event_url': u'{0}/{1}/organizer/event/{2}'.format(settings.SITE_URL, vosae_event.tenant.slug, unicode(vosae_event.id))
    }

    # Schedule next reminder
    vosae_event._set_next_reminder()
    vosae_event.update(set__next_reminder=vosae_event.next_reminder)
    vosae_event.check_immediate_reminders_emit()

    # Saves notifications
    for recipient in reminders['POPUP']:
        notifications.EventReminder(
            tenant=vosae_event.tenant,
            recipient=DBRef('vosae_user', ObjectId(recipient)),
            vosae_event=vosae_event,
            occurs_at=start,
            summary=vosae_event.summary
        ).save()

    # Send mails
    connection = get_connection()
    for language, emails in reminders['EMAIL'].items():
        with respect_language(language):
            plaintext_context = Context(autoescape=False)  # HTML escaping not appropriate in plaintext
            subject = render_to_string('organizer/emails/organizer_reminder_subject.txt', context, plaintext_context)
            subject = ''.join(subject.splitlines())
            text_body = render_to_string('organizer/emails/organizer_reminder_content.txt', context, plaintext_context)
            html_body = render_to_string('organizer/emails/organizer_reminder_content.html', context)

            message = EmailMultiAlternatives(subject, text_body, cc=emails, connection=connection) # Mandrill doesn't support BCC so we have to use CC without preserving recipients
            message.attach_alternative(html_body, "text/html")
            message.preserve_recipients = False # Useful for Mandrill
            message.send()
