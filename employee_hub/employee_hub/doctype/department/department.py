# Copyright (c) 2026, Renish Ponkiya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class Department(Document):
    def validate(self):
        self.validate_duplicate_department_name()

    def validate_duplicate_department_name(self):
        """Prevent duplicate department names (case-insensitive)."""

        existing = frappe.db.sql("""
            SELECT name
            FROM `tabDepartment`
            WHERE LOWER(department_name) = LOWER(%s)
            AND name != %s
            LIMIT 1
        """, (self.department_name, self.name))

        if existing:
            frappe.throw(_("Department Name already exists (case-insensitive duplicate not allowed)."))