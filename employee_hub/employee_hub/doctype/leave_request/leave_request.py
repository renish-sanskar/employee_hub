# Copyright (c) 2026, Renish Ponkiya and contributors
# For license information, please see license.txt

# your_app/your_app/doctype/leave_request/leave_request.py

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import getdate, now_datetime


class LeaveRequest(Document):
    def validate(self):
        self.validate_dates()
        self.calculate_total_days()

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