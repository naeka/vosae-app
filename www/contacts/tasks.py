# -*- coding:Utf-8 -*-

from celery.task import task


@task()
def entity_saved_task(document, created, issuer):
    from contacts.models import Contact, Organization
    from timeline import models as timeline_entries
    from notification import models as notifications
    # Create notification and timeline entries
    notification_list = []
    if type(document) is Contact:
        timeline_entry = timeline_entries.ContactSaved(
            tenant=document.tenant,
            contact=document,
            issuer=issuer,
            created=created
        )
        if not created:
            for subscriber in set(document.subscribers).difference([issuer]):
                notification_list.append(notifications.ContactSaved(
                    tenant=document.tenant,
                    recipient=subscriber,
                    issuer=issuer,
                    contact=document
                ))
    elif type(document) is Organization:
        timeline_entry = timeline_entries.OrganizationSaved(
            tenant=document.tenant,
            organization=document,
            issuer=issuer,
            created=created
        )
        if not created:
            for subscriber in set(document.subscribers).difference([issuer]):
                notification_list.append(notifications.OrganizationSaved(
                    tenant=document.tenant,
                    recipient=subscriber,
                    issuer=issuer,
                    organization=document
                ))
    timeline_entry.save()
    for notification in notification_list:
        notification.save()
