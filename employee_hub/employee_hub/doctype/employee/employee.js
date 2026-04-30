// Copyright (c) 2026, Renish Ponkiya and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee", {
	// Runs every time the form is loaded or refreshed. We re-apply the
	// designation query here so the filter is active on existing records too.
	refresh(frm) {
		frm.trigger("set_designation_query");
	},

	// Triggered when the Department field changes. Clearing designation
	// prevents an inconsistent (department, designation) pair from lingering,
	// then we re-bind the query so the dropdown reflects the new department.
	department(frm) {
		frm.set_value("designation", null);
		frm.trigger("set_designation_query");
	},

	// Restricts the Designation link field to designations belonging to the
	// currently selected department. Note: this assumes the Designation
	// doctype has a `department` link field (add a Custom Field if needed).
	set_designation_query(frm) {
		frm.set_query("designation", () => {
			return {
				filters: {
					department: frm.doc.department || "",
				},
			};
		});
	},
});
