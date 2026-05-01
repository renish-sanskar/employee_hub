# Copyright (c) 2026, Renish Ponkiya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import getdate, now_datetime, today


LEAVE_TYPE_LIMIT_FIELD = {
    "Casual Leave": "max_casual_leave",
    "Sick Leave": "max_sick_leave",
    "Earned Leave": "max_earned_leave",
    # Compensatory Leave has no per-type cap in the configuration.
}


def get_permission_query_conditions(user=None):
    if not user:
        user = frappe.session.user

    if user == "Administrator" or "HR Manager" in frappe.get_roles(user):
        return ""

    safe_user = frappe.db.escape(user)

    return (
        f"(`tabLeave Request`.employee IN "
        f"(SELECT name FROM `tabEmployee` WHERE employee_email = {safe_user}))"
    )


class LeaveRequest(Document):
    def validate(self):
        self.validate_employee_is_self()
        self.validate_dates()
        self.calculate_total_days()
        self.validate_against_leave_configuration()

    def validate_employee_is_self(self):
        """Non-HR users may only file leave requests for themselves."""
        user = frappe.session.user

        # Administrator and HR Manager can file on behalf of anyone.
        if user == "Administrator" or "HR Manager" in frappe.get_roles(user):
            return

        if not self.employee:
            return

        employee_email = frappe.db.get_value("Employee", self.employee, "employee_email")
        if employee_email != user:
            frappe.throw(_("You can only create leave requests for yourself."))

    def on_submit(self):
        # Employee submits request → enters Pending state
        self.approval_status = "Pending"

    def on_update(self):
        """
        Handle leave balance movement based on workflow state change.

        Rules:
        - Pending   → deduct leave balance
        - Approved  → no change (already deducted in Pending)
        - Rejected  → add leave balance back
        - Cancelled → add leave balance back
        """
        old_doc = self.get_doc_before_save()
        previous_status = old_doc.approval_status if old_doc else None
        current_status = self.approval_status

        if previous_status == current_status:
            return

        # Deduct leave when request enters Pending
        if current_status == "Pending":
            self.update_leave_balance(-self.total_days)

        # Add leave back when request is Rejected or Cancelled
        elif current_status in ["Rejected", "Cancelled"]:
            self.update_leave_balance(self.total_days)

    def update_leave_balance(self, days):
        """Update employee leave balance."""
        annual_leave_balance = frappe.db.get_value("Employee", self.employee, "annual_leave_balance") or 0
        new_balance = annual_leave_balance + days

        if new_balance < 0:
            frappe.throw(_("Insufficient leave balance."))

        frappe.db.set_value("Employee", self.employee, "annual_leave_balance", new_balance)

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
        """
        Apply rules sourced from the Leave Configuration single doctype.
        """
        config = frappe.get_cached_doc("Leave Configuration")

        # 1) Backdated leave guard
        if (
            self.from_date
            and not config.allow_backdated_leave
            and getdate(self.from_date) < getdate(today())
        ):
            frappe.throw(_("Backdated leave requests are not allowed."))

        # 2) Per-request maximum
        max_per_request = config.max_leave_days_per_request or 0
        if max_per_request and (self.total_days or 0) > max_per_request:
            frappe.throw(
                _("Total Days ({0}) exceeds the maximum allowed per request ({1}).").format(
                    self.total_days, max_per_request
                )
            )

        # 3) Per-leave-type maximum
        limit_field = LEAVE_TYPE_LIMIT_FIELD.get(self.leave_type)
        if limit_field:
            type_limit = config.get(limit_field) or 0
            if type_limit and (self.total_days or 0) > type_limit:
                frappe.throw(
                    _("{0} cannot exceed {1} day(s) per request.").format(
                        self.leave_type, type_limit
                    )
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