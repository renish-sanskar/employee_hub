# Copyright (c) 2026, Renish Ponkiya and contributors
# For license information, please see license.txt

# your_app/your_app/doctype/designation/designation.py

import frappe
from frappe.model.document import Document
from frappe import _


class Designation(Document):
    # Runs on every save. Centralises validations for Designation.
    def validate(self):
        self.validate_duplicate_designation_name()

    def validate_duplicate_designation_name(self):
        """Prevent duplicate designation names (case-insensitive)."""

        # Nothing to compare against if the field is empty; a `reqd` flag
        # at the schema level should already enforce presence.
        if not self.designation_name:
            return

        # Case-insensitive duplicate check. `name != %s` excludes the current
        # row so re-saving an existing record doesn't trigger a false match.
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