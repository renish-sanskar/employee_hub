# Copyright (c) 2026, Renish Ponkiya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import getdate, now_datetime, today


# Maps the user-facing Leave Type select option to the matching
# limit field on the Leave Configuration single doctype.
LEAVE_TYPE_LIMIT_FIELD = {
    "Casual Leave": "max_casual_leave",
    "Sick Leave": "max_sick_leave",
    "Earned Leave": "max_earned_leave",
    # Compensatory Leave has no per-type cap in the configuration.
}


class LeaveRequest(Document):
    def validate(self):
        self.validate_dates()
        self.calculate_total_days()
        self.validate_against_leave_configuration()

    def on_submit(self):
        self.approval_status = "Pending"

    def validate_dates(self):
        """Validate leave date range."""

        if not self.from_date or not self.to_date:
            return

        if getdate(self.from_date) > getdate(self.to_date):
            frappe.throw(_("From Date cannot be greater than To Date."))

    def calculate_total_days(self):
        """Auto-calculate total leave days."""

        if not self.from_date or not self.to_date:
            self.total_days = 0
            return

        from_date = getdate(self.from_date)
        to_date = getdate(self.to_date)

        self.total_days = (to_date - from_date).days + 1

    def validate_against_leave_configuration(self):
        """Apply rules sourced from the Leave Configuration single doctype.

        Centralising these checks here means admins can tweak limits at
        runtime without code changes.
        """

        # Pull all config values in one trip; falls back to an empty doc
        # if the single hasn't been initialised yet.
        config = frappe.get_cached_doc("Leave Configuration")

        # 1) Backdated leave guard.
        if (
            self.from_date
            and not config.allow_backdated_leave
            and getdate(self.from_date) < getdate(today())
        ):
            frappe.throw(_("Backdated leave requests are not allowed."))

        # 2) Per-request maximum.
        max_per_request = config.max_leave_days_per_request or 0
        if max_per_request and (self.total_days or 0) > max_per_request:
            frappe.throw(
                _("Total Days ({0}) exceeds the maximum allowed per request ({1}).")
                .format(self.total_days, max_per_request)
            )

        # 3) Per-leave-type maximum (skip for types not tracked in config).
        limit_field = LEAVE_TYPE_LIMIT_FIELD.get(self.leave_type)
        if limit_field:
            type_limit = config.get(limit_field) or 0
            if type_limit and (self.total_days or 0) > type_limit:
                frappe.throw(
                    _("{0} cannot exceed {1} day(s) per request.")
                    .format(self.leave_type, type_limit)
                )

    def approve_leave(self):
        """Approve leave request."""

        self.approval_status = "Approved"
        self.approved_by = frappe.session.user
        self.approval_date = now_datetime()
        self.save()

    def reject_leave(self, rejection_reason=None):
        """Reject leave request."""

        self.approval_status = "Rejected"
        self.approved_by = frappe.session.user
        self.approval_date = now_datetime()
        self.rejection_reason = rejection_reason
        self.save()