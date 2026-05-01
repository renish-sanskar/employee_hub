// Copyright (c) 2026, Renish Ponkiya and contributors
// For license information, please see license.txt

frappe.ui.form.on("Leave Request", {
	refresh(frm) {
		frm.trigger("show_leave_balance");
		frm.trigger("prefill_and_lock_employee");
	},

	// Pre-fill `employee` with the Employee record linked to the logged-in user.
	// Non-HR Managers cannot change it -> they can only file leave for themselves.
	prefill_and_lock_employee(frm) {
		const is_hr_manager = frappe.user.has_role("HR Manager");

		// HR Manager / Administrator can pick any employee.
		if (is_hr_manager) {
			frm.set_df_property("employee", "read_only", 0);
			return;
		}

		// For new docs without an employee, look up the Employee by email
		// of the currently logged-in user and set it.
		if (frm.is_new() && !frm.doc.employee) {
			frappe.db.get_value(
				"Employee",
				{ employee_email: frappe.session.user },
				"name"
			).then(r => {
				const employee = r.message && r.message.name;
				if (employee) {
					frm.set_value("employee", employee);
				} else {
					frappe.show_alert({
						message: __("No Employee record is linked to your user ({0}).", [frappe.session.user]),
						indicator: "red"
					}, 7);
				}
			});
		}

		// Lock the field so the user cannot switch to another employee.
		frm.set_df_property("employee", "read_only", 1);
	},

	// Show remaining leave balance as a form intro when employee changes
	employee(frm) {
		if (!frm.doc.employee) {
			frm.set_intro("");
			return;
		}


		frm.trigger("show_leave_balance");
	},


	show_leave_balance(frm) {
		if (!frm.doc.employee) return;

		frappe.db.get_value("Employee", frm.doc.employee, ["full_name", "annual_leave_balance"])
			.then(r => {
				const d = r.message || {};
				const balance = d.annual_leave_balance ?? 0;
				const name = d.full_name || frm.doc.employee;

				const color = balance <= 0 ? "red" : balance <= 5 ? "orange" : "blue";
				frm.set_intro(
					`${name} has ${balance} leave day(s) remaining.`,
					color
				);
			});
	},

	// Auto-calculate total_days when either date changes
	from_date(frm) {
		frm.trigger("calculate_total_days");
	},

	to_date(frm) {
		frm.trigger("calculate_total_days");
	},

	calculate_total_days(frm) {
		const { from_date, to_date } = frm.doc;
		if (!from_date || !to_date) {
			frm.set_value("total_days", 0);
			return;
		}

		if (frappe.datetime.get_diff(to_date, from_date) < 0) {
			frm.set_value("total_days", 0);
			frappe.show_alert({
				message: __("To Date cannot be before From Date"),
				indicator: "red"
			}, 5);
			return;
		}

		// Inclusive of both endpoints
		const days = frappe.datetime.get_diff(to_date, from_date) + 1;
		frm.set_value("total_days", days);

		frm.trigger("check_max_leave_days");
	},

	// Warn if request exceeds configured per-request limit
	check_max_leave_days(frm) {
		if (!frm.doc.total_days) return;

		frappe.db.get_single_value("Leave Configuration", "max_leave_days_per_request")
			.then(max_days => {
				if (max_days && frm.doc.total_days > max_days) {
					frappe.show_alert({
						message: __("Total Days ({0}) exceeds the maximum allowed per request ({1}).",
							[frm.doc.total_days, max_days]),
						indicator: "orange"
					}, 7);
				}
			});
	},

	// Confirmation dialog before submission with a summary of the request
	before_submit(frm) {
		frappe.validated = false;

		const summary = `
			<div style="line-height: 1.8;">
				<b>Employee:</b> ${frappe.utils.escape_html(frm.doc.employee_name || frm.doc.employee || "")}<br>
				<b>Leave Type:</b> ${frappe.utils.escape_html(frm.doc.leave_type || "")}<br>
				<b>From:</b> ${frappe.datetime.str_to_user(frm.doc.from_date) || ""}<br>
				<b>To:</b> ${frappe.datetime.str_to_user(frm.doc.to_date) || ""}<br>
				<b>Total Days:</b> ${frm.doc.total_days || 0}<br>
				<b>Reason:</b> ${frappe.utils.escape_html(frm.doc.reason || "")}
			</div>
		`;

		return new Promise(resolve => {
			frappe.confirm(
				`Submit this leave request?<br><br>${summary}`,
				() => {
					frappe.validated = true;
					resolve();
				},
				() => resolve()
			);
		});
	}
});

