# -*- coding:Utf-8 -*-

from mongoengine.base import ValidationError


__all__ = (
    'InvalidInvoiceBaseState',
    'InvalidTaxRate',
    'InvalidDownPaymentPercentage',
    'InvalidDownPaymentDueDate',
    'NotDeletableInvoice',
    'NotIssuableInvoice',
    'NotCancelableInvoice',
    'NotModifiableInvoice',
    'NotPayableInvoice',
    'InvalidPaymentAmount'
)


class InvalidInvoiceBaseState(ValidationError):

    """Used on :class:`~invoicing.models.InvoiceBase` objects when can not set state."""
    pass


class InvalidTaxRate(ValidationError):

    """
    Used on :class:`~invoicing.models.Tax` objects that have a rate attribute which can
    not be modified.
    """
    pass


class NotIssuableInvoice(ValidationError):

    """Used on :class:`~invoicing.models.InvoiceBase` objects when they are not issuable."""
    pass


class InvalidDownPaymentPercentage(ValidationError):

    """
    Used on :class:`~invoicing.models.DownPaymentInvoice` objects when the given percentage is
    invalid.
    """

    def __init__(self, message="", **kwargs):
        super(InvalidDownPaymentPercentage, self).__init__(message, **kwargs)
        self.message = 'Invalid down-payment percentage:\n%s' % message


class InvalidDownPaymentDueDate(ValidationError):

    """Used on :class:`~invoicing.models.DownPaymentInvoice` objects when due date is invalid."""
    pass


class NotDeletableInvoice(Exception):

    """Used on :class:`~invoicing.models.InvoiceBase` objects when they are not deletable."""
    pass


class NotModifiableInvoice(Exception):

    """Used on :class:`~invoicing.models.Invoice` objects when they are not modifiable."""
    pass


class NotCancelableInvoice(Exception):

    """Used on :class:`~invoicing.models.Invoice` objects when they are not cancelable."""
    pass


class NotPayableInvoice(Exception):

    """Used on :class:`~invoicing.models.Invoice` objects when they are not payable."""
    pass


class InvalidPaymentAmount(ValidationError):

    """Used on payment-related objects when the given payment amount is invalid."""

    def __init__(self, message="", **kwargs):
        super(InvalidPaymentAmount, self).__init__(message, **kwargs)
        self.message = 'Invalid payment amount:\n%s' % message
