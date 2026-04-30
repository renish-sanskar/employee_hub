# Copyright (c) 2026, Renish Ponkiya and contributors
# For license information, please see license.txt

# your_app/your_app/doctype/designation/designation.py

import frappe
from frappe.model.document import Document
from frappe import _


class Designation(Document):
    def validate(self):
        self.validate_duplicate_designation_name()

    def validate_duplicate_designation_name(self):
        """Prevent duplicate designation names (case-insensitive)."""

        if not self.designation_name:
            return

        existing = frappe.db.sql("""
            SELECT name
            FROM `tabDesignation`
            WHERE LOWER(designation_name) = LOWER(%s)
              AND name != %s
            LIMIT 1
        """, (self.designation_name, self.name))

        if existing:
            frappe.throw(
                _("Designation Name already exists (case-insensitive duplicate not allowed).")
            )