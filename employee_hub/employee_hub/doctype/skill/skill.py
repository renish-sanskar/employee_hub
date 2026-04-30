# Copyright (c) 2026, Renish Ponkiya and contributors
# For license information, please see license.txt

# your_app/your_app/doctype/skill/skill.py

import frappe
from frappe.model.document import Document
from frappe import _


class Skill(Document):
    def validate(self):
        self.validate_duplicate_skill_name()

    def validate_duplicate_skill_name(self):
        """Prevent duplicate skill names (case-insensitive)."""

        if not self.skill_name:
            return

        existing = frappe.db.sql("""
            SELECT name
            FROM `tabSkill`
            WHERE LOWER(skill_name) = LOWER(%s)
              AND name != %s
            LIMIT 1
        """, (self.skill_name, self.name))

        if existing:
            frappe.throw(
                _("Skill Name already exists (case-insensitive duplicate not allowed).")
            )