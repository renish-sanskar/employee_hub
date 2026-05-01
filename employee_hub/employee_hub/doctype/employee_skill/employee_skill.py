# Copyright (c) 2026, Renish Ponkiya and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


# Child table doctype attached to Employee.employee_skill.
# No standalone validations needed — lifecycle is driven entirely by the
# parent Employee document, so this controller is intentionally empty.
class EmployeeSkill(Document):
	pass
