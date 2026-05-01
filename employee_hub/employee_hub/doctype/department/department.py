# Copyright (c) 2026, Renish Ponkiya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class Department(Document):
    # Runs on every save (insert + update). Single hook point for all
    # business validations on Department.
    def validate(self):
        self.validate_duplicate_department_name()

    def validate_duplicate_department_name(self):
        """Prevent duplicate department names (case-insensitive)."""

        # Frappe's `unique` flag on a field is case-sensitive at the DB level,
        # so we run an explicit case-insensitive lookup. The `name != %s`
        # clause excludes the current record so updates don't match themselves.
        existing = frappe.db.sql("""
            SELECT name
            FROM `tabDepartment`
            WHERE LOWER(department_name) = LOWER(%s)
            AND name != %s
            LIMIT 1
        """, (self.department_name, self.name))

        if existing:
            frappe.throw(_("Department Name already exists (case-insensitive duplicate not allowed)."))