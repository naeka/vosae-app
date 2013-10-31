# -*- coding:Utf-8 -*-

from mongoengine import signals
from timeline.models.base import TimelineEntry
from timeline.models.invoicing_entries.invoicing_timeline_entry import InvoicingTimelineEntry

from timeline.models.invoicing_entries import invoicebase_saved
from timeline.models.invoicing_entries.invoicebase_saved import *
from timeline.models.invoicing_entries import invoicebase_changed_state
from timeline.models.invoicing_entries.invoicebase_changed_state import *
from timeline.models.invoicing_entries import quotation_make_invoice
from timeline.models.invoicing_entries.quotation_make_invoice import *
from timeline.models.invoicing_entries import invoice_cancelled
from timeline.models.invoicing_entries.invoice_cancelled import *


__all__ = (
    invoicebase_saved.__all__ +
    invoicebase_changed_state.__all__ +
    quotation_make_invoice.__all__ +
    invoice_cancelled.__all__
)


"""
SIGNALS
"""


signals.pre_save.connect(InvoicingTimelineEntry.pre_save_quotation, sender=QuotationSaved)
signals.pre_save.connect(InvoicingTimelineEntry.pre_save_quotation, sender=QuotationChangedState)
signals.pre_save.connect(InvoicingTimelineEntry.pre_save_quotation, sender=QuotationMakeInvoice)
signals.pre_save.connect(InvoicingTimelineEntry.pre_save_quotation, sender=QuotationMakeDownPaymentInvoice)

signals.pre_save.connect(InvoicingTimelineEntry.pre_save_invoice, sender=InvoiceSaved)
signals.pre_save.connect(InvoicingTimelineEntry.pre_save_invoice, sender=InvoiceChangedState)
signals.pre_save.connect(InvoicingTimelineEntry.pre_save_invoice, sender=InvoiceCancelled)

signals.pre_save.connect(InvoicingTimelineEntry.pre_save_down_payment_invoice, sender=DownPaymentInvoiceSaved)
signals.pre_save.connect(InvoicingTimelineEntry.pre_save_down_payment_invoice, sender=DownPaymentInvoiceChangedState)
signals.pre_save.connect(InvoicingTimelineEntry.pre_save_down_payment_invoice, sender=DownPaymentInvoiceCancelled)

signals.pre_save.connect(InvoicingTimelineEntry.pre_save_credit_note, sender=CreditNoteSaved)
signals.pre_save.connect(InvoicingTimelineEntry.pre_save_credit_note, sender=CreditNoteChangedState)


signals.post_save.connect(TimelineEntry.post_save, sender=QuotationSaved)
signals.post_save.connect(TimelineEntry.post_save, sender=QuotationChangedState)
signals.post_save.connect(TimelineEntry.post_save, sender=QuotationMakeInvoice)
signals.post_save.connect(TimelineEntry.post_save, sender=QuotationMakeDownPaymentInvoice)
signals.post_save.connect(TimelineEntry.post_save, sender=InvoiceSaved)
signals.post_save.connect(TimelineEntry.post_save, sender=InvoiceChangedState)
signals.post_save.connect(TimelineEntry.post_save, sender=InvoiceCancelled)
signals.post_save.connect(TimelineEntry.post_save, sender=DownPaymentInvoiceSaved)
signals.post_save.connect(TimelineEntry.post_save, sender=DownPaymentInvoiceChangedState)
signals.post_save.connect(TimelineEntry.post_save, sender=DownPaymentInvoiceCancelled)
signals.post_save.connect(TimelineEntry.post_save, sender=CreditNoteSaved)
signals.post_save.connect(TimelineEntry.post_save, sender=CreditNoteChangedState)
