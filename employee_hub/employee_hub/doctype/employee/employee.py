# Copyright (c) 2026, Renish Ponkiya and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today, validate_email_address


class Employee(Document):
    # Runs just before the document is saved to the database.
    # Used here to keep `full_name` in sync with first/last name.
    def before_save(self):
        self.set_full_name()

    # Runs once when the document is first inserted into the DB.
    # Used to seed defaults that depend on global configuration so we
    # don't hard-code values inside the schema.
    def before_insert(self):
        self.set_default_leave_balance()

    # Runs on every save (insert + update) before `before_save`.
    # Centralises all business-rule validations for the Employee doctype.
    def validate(self):
        # Recompute full_name early so it is also correct on insert.
        self.set_full_name()
        self.validate_date_of_birth()
        self.validate_date_of_joining()
        self.validate_employee_email()
        self.validate_joining_after_birth()
        self.validate_to_edit_details()

    def set_full_name(self):
        """Auto-generate full name from first_name + last_name."""

        # Strip whitespace and treat None as empty string so we never
        # concatenate "None" into the final value.
        first = (self.first_name or "").strip()
        last = (self.last_name or "").strip()

        # Join only the non-empty parts to avoid a stray leading/trailing space
        # when one of the names is missing.
        self.full_name = " ".join(part for part in [first, last] if part)

    def set_default_leave_balance(self):
        """Seed annual_leave_balance from the Leave Configuration single."""

        # Only seed if the user hasn't already set a value on the form.
        if self.annual_leave_balance:
            return

        # Use cached single value to avoid a fresh DB read on every insert.
        default_balance = frappe.db.get_single_value(
            "Leave Configuration", "default_annual_balance"
        )
        if default_balance is not None:
            self.annual_leave_balance = default_balance

    def validate_date_of_birth(self):
        # Skip validation if DOB is not provided; the `reqd` flag on the
        # field already enforces presence at the schema level.
        if not self.date_of_birth:
            return

        dob = getdate(self.date_of_birth)
        today_date = getdate(today())

        # Compute age in completed years. The boolean subtraction handles
        # the case where the birthday has not yet occurred this year.
        age_years = (
            today_date.year
            - dob.year
            - ((today_date.month, today_date.day) < (dob.month, dob.day))
        )

        # Business rule: employees must be legal adults (18+).
        if age_years < 18:
            frappe.throw(_("Employee must be at least 18 years old."))

    def validate_date_of_joining(self):
        if not self.date_of_joining:
            return

        # Joining date cannot be set to a future date — employees can only
        # be onboarded on or before today.
        if getdate(self.date_of_joining) > getdate(today()):
            frappe.throw(_("Date of Joining cannot be in the future."))

    def validate_employee_email(self):
        if not self.employee_email:
            return

        # Delegate format checking to Frappe's built-in validator so we
        # stay consistent with the rest of the framework. `throw=True`
        # raises a ValidationError on a malformed address.
        validate_email_address(self.employee_email, throw=True)

    def validate_joining_after_birth(self):
        # Both fields are required to make the comparison meaningful.
        if not (self.date_of_birth and self.date_of_joining):
            return

        # Sanity check: an employee cannot join on or before they were born.
        if getdate(self.date_of_joining) <= getdate(self.date_of_birth):
            frappe.throw(_("Date of Joining must be after Date of Birth."))
            
    def validate_to_edit_details(self):
        if "Employee" in frappe.get_roles() and "HR Admin" not in frappe.get_roles():
            if self.employee_email != frappe.session.user:
                frappe.throw("You can only edit your own Employee record.")