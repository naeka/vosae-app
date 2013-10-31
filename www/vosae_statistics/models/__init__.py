# -*- coding:Utf-8 -*-

from mongoengine import signals

from vosae_statistics.models import statistics
from vosae_statistics.models.statistics import *


__all__ = (
    statistics.__all__ +
    ()
)


"""
SIGNALS
"""


signals.post_save.connect(Statistics.post_save, sender=InvoiceStatistics)
signals.post_save.connect(Statistics.post_save, sender=DownPaymentInvoiceStatistics)
signals.post_save.connect(Statistics.post_save, sender=CreditNoteStatistics)
