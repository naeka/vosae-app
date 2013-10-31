# -*- coding:Utf-8 -*-

from celery.task import periodic_task, task
from celery.schedules import crontab

from timeline import models as timeline_entries
from notification import models as notifications


@periodic_task(run_every=crontab(hour=0, minute=0, day_of_week="*"))
def update_invoices_states():
    from invoicing.models import Quotation, Invoice
    Quotation.manage_states()
    Invoice.manage_states()


@task()
def invoicebase_saved_task(document, created):
    notification_list = []
    if document.is_quotation():
        timeline_entry = timeline_entries.QuotationSaved(
            tenant=document.tenant,
            issuer=document.current_revision.issuer,
            quotation=document,
            created=created
        )
        if not created:
            for subscriber in set(document.subscribers).difference([document.current_revision.issuer]):
                notification_list.append(notifications.QuotationSaved(
                    tenant=document.tenant,
                    recipient=subscriber,
                    issuer=document.current_revision.issuer,
                    quotation=document,
                    created=created
                ))
    elif document.is_invoice():
        timeline_entry = timeline_entries.InvoiceSaved(
            tenant=document.tenant,
            issuer=document.current_revision.issuer,
            invoice=document,
            created=created
        )
        if not created:
            for subscriber in set(document.subscribers).difference([document.current_revision.issuer]):
                notification_list.append(notifications.InvoiceSaved(
                    tenant=document.tenant,
                    recipient=subscriber,
                    issuer=document.current_revision.issuer,
                    invoice=document,
                    created=created
                ))
    elif document.is_down_payment_invoice():
        timeline_entry = timeline_entries.DownPaymentInvoiceSaved(
            tenant=document.tenant,
            issuer=document.current_revision.issuer,
            down_payment_invoice=document,
            created=created
        )
        if not created:
            for subscriber in set(document.subscribers).difference([document.current_revision.issuer]):
                notification_list.append(notifications.DownPaymentInvoiceSaved(
                    tenant=document.tenant,
                    recipient=subscriber,
                    issuer=document.current_revision.issuer,
                    down_payment_invoice=document,
                    created=created
                ))
    elif document.is_credit_note():
        timeline_entry = timeline_entries.CreditNoteSaved(
            tenant=document.tenant,
            issuer=document.current_revision.issuer,
            credit_note=document,
            created=created
        )
        if not created:
            for subscriber in set(document.subscribers).difference([document.current_revision.issuer]):
                notification_list.append(notifications.CreditNoteSaved(
                    tenant=document.tenant,
                    recipient=subscriber,
                    issuer=document.current_revision.issuer,
                    credit_note=document,
                    created=created
                ))
    timeline_entry.save()
    for notification in notification_list:
        notification.save()


@task()
def invoicebase_changed_state_task(document, previous_state):
    notification_list = []
    if document.is_quotation():
        timeline_entry = timeline_entries.QuotationChangedState(
            tenant=document.tenant,
            issuer=document.current_revision.issuer,
            quotation=document,
            previous_state=previous_state,
            new_state=document.state
        )
        for subscriber in set(document.subscribers).difference([document.current_revision.issuer]):
            notification_list.append(notifications.QuotationChangedState(
                tenant=document.tenant,
                recipient=subscriber,
                issuer=document.current_revision.issuer,
                quotation=document,
                previous_state=previous_state,
                new_state=document.state
            ))
    elif document.is_invoice():
        timeline_entry = timeline_entries.InvoiceChangedState(
            tenant=document.tenant,
            issuer=document.current_revision.issuer,
            invoice=document,
            previous_state=previous_state,
            new_state=document.state
        )
        for subscriber in set(document.subscribers).difference([document.current_revision.issuer]):
            notification_list.append(notifications.CreditNoteChangedState(
                tenant=document.tenant,
                recipient=subscriber,
                issuer=document.current_revision.issuer,
                invoice=document,
                previous_state=previous_state,
                new_state=document.state
            ))
    elif document.is_down_payment_invoice():
        timeline_entry = timeline_entries.DownPaymentInvoiceChangedState(
            tenant=document.tenant,
            issuer=document.current_revision.issuer,
            down_payment_invoice=document,
            previous_state=previous_state,
            new_state=document.state
        )
        for subscriber in set(document.subscribers).difference([document.current_revision.issuer]):
            notification_list.append(notifications.CreditNoteChangedState(
                tenant=document.tenant,
                recipient=subscriber,
                issuer=document.current_revision.issuer,
                down_payment_invoice=document,
                previous_state=previous_state,
                new_state=document.state
            ))
    elif document.is_credit_note():
        timeline_entry = timeline_entries.CreditNoteChangedState(
            tenant=document.tenant,
            issuer=document.current_revision.issuer,
            credit_note=document,
            previous_state=previous_state,
            new_state=document.state
        )
        for subscriber in set(document.subscribers).difference([document.current_revision.issuer]):
            notification_list.append(notifications.CreditNoteChangedState(
                tenant=document.tenant,
                recipient=subscriber,
                issuer=document.current_revision.issuer,
                credit_note=document,
                previous_state=previous_state,
                new_state=document.state
            ))
    timeline_entry.save()
    for notification in notification_list:
        notification.save()


@task()
def post_make_invoice_task(document, invoice_or_down_payment_invoice):
    notification_list = []
    if invoice_or_down_payment_invoice.is_invoice():
        timeline_entry = timeline_entries.QuotationMakeInvoice(
            tenant=document.tenant,
            issuer=document.current_revision.issuer,
            quotation=document,
            invoice=invoice_or_down_payment_invoice
        )
        for subscriber in set(document.subscribers).difference([document.current_revision.issuer]):
            notification_list.append(notifications.QuotationMakeInvoice(
                tenant=document.tenant,
                recipient=subscriber,
                issuer=document.current_revision.issuer,
                quotation=document,
                invoice=invoice_or_down_payment_invoice
            ))
    elif invoice_or_down_payment_invoice.is_down_payment_invoice():
        timeline_entry = timeline_entries.QuotationMakeDownPaymentInvoice(
            tenant=document.tenant,
            issuer=document.current_revision.issuer,
            quotation=document,
            down_payment_invoice=invoice_or_down_payment_invoice
        )
        for subscriber in set(document.subscribers).difference([document.current_revision.issuer]):
            notification_list.append(notifications.QuotationMakeDownPaymentInvoice(
                tenant=document.tenant,
                recipient=subscriber,
                issuer=document.current_revision.issuer,
                quotation=document,
                down_payment_invoice=invoice_or_down_payment_invoice
            ))
        timeline_entry.save()
        for notification in notification_list:
            notification.save()


@task()
def post_register_invoice_task(document, previous_state):
    from vosae_statistics.models import InvoiceStatistics
    InvoiceStatistics(
        tenant=document.tenant,
        date=document.current_revision.invoicing_date,
        amount=document.amount,
        organization=document.organization,
        contact=document.contact,
        location=document.current_revision.billing_address if document.account_type == 'RECEIVABLE' else document.current_revision.sender_address,
        account_type=document.account_type,
        invoice=document
    ).save()


@task()
def post_cancel_invoice_task(document, credit_note):
    notification_list = []
    if document.is_invoice():
        timeline_entry = timeline_entries.InvoiceCancelled(
            tenant=document.tenant,
            issuer=document.current_revision.issuer,
            invoice=document,
            credit_note=credit_note
        )
        for subscriber in set(document.subscribers).difference([document.current_revision.issuer]):
            notification_list.append(notifications.InvoiceCancelled(
                tenant=document.tenant,
                recipient=subscriber,
                issuer=document.current_revision.issuer,
                invoice=document,
                credit_note=credit_note
            ))
    elif document.is_down_payment_invoice():
        timeline_entry = timeline_entries.DownPaymentInvoiceCancelled(
            tenant=document.tenant,
            issuer=document.current_revision.issuer,
            down_payment_invoice=document,
            credit_note=credit_note
        )
        for subscriber in set(document.subscribers).difference([document.current_revision.issuer]):
            notification_list.append(notifications.DownPaymentInvoiceCancelled(
                tenant=document.tenant,
                recipient=subscriber,
                issuer=document.current_revision.issuer,
                down_payment_invoice=document,
                credit_note=credit_note
            ))
    timeline_entry.save()
    for notification in notification_list:
        notification.save()


@task()
def invoicebase_deleted_task(document):
    from timeline.models import TimelineEntry
    from notification.models import Notification
    if document.is_quotation():
        TimelineEntry.objects.filter(tenant=document.tenant, quotation=document).delete()
        Notification.objects.filter(tenant=document.tenant, quotation=document).delete()
    elif document.is_invoice():
        TimelineEntry.objects.filter(tenant=document.tenant, invoice=document).delete()
        Notification.objects.filter(tenant=document.tenant, invoice=document).delete()
    elif document.is_down_payment_invoice():
        TimelineEntry.objects.filter(tenant=document.tenant, down_payment_invoice=document).delete()
        Notification.objects.filter(tenant=document.tenant, down_payment_invoice=document).delete()
    elif document.is_credit_note():
        TimelineEntry.objects.filter(tenant=document.tenant, credit_note=document).delete()
        Notification.objects.filter(tenant=document.tenant, credit_note=document).delete()
