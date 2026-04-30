// Copyright (c) 2026, Renish Ponkiya and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee", {
	// Runs every time the form is loaded or refreshed
	refresh(frm) {
		frm.trigger("set_designation_query");
		frm.trigger("set_dashboard_indicator");
		frm.trigger("add_leave_request_button");
		frm.trigger("add_skills_summary_button");
	},

	// Clear designation when department changes
	department(frm) {
		frm.set_value("designation", null);
		frm.trigger("set_designation_query");
	},

	// Auto-generate full name
	first_name(frm) {
		frm.trigger("set_full_name");
	},

	last_name(frm) {
		frm.trigger("set_full_name");
	},

	// Restrict designation by selected department
	set_designation_query(frm) {
		frm.set_query("designation", () => {
			return {
				filters: {
					department: frm.doc.department || "",
					is_active: 1
				}
			};
		});
	},

	// Auto-generate full_name from first_name + last_name
	set_full_name(frm) {
		const first = (frm.doc.first_name || "").trim();
		const last = (frm.doc.last_name || "").trim();
		const full_name = [first, last].filter(Boolean).join(" ");

		frm.set_value("full_name", full_name);
	},

	// Dashboard indicator: short, meaningful toast that auto-hides after 5s
	set_dashboard_indicator(frm) {
		if (frm.is_new() || !frm.doc.employee_status) return;

		const status_color_map = {
			"Active": "green",
			"On Leave": "orange",
			"Inactive": "gray",
			"Terminated": "red"
		};

		const color = status_color_map[frm.doc.employee_status] || "gray";
		const name = frm.doc.full_name || frm.doc.name;
		const leaves = frm.doc.annual_leave_balance ?? 0;

		const message = `<b>${frappe.utils.escape_html(name)}</b> is <b>${frm.doc.employee_status}</b> &middot; ${leaves} leaves left`;

		// 3rd arg = seconds visible
		frappe.show_alert({ message: message, indicator: color }, 5);
	},

	// Custom button: Create Leave Request
	add_leave_request_button(frm) {
		if (frm.is_new()) return;

		frm.add_custom_button("Create Leave Request", () => {
			frappe.route_options = {
				employee: frm.doc.name
			};

			frappe.new_doc("Leave Request");
		});
	},

	// Custom button: View Skills Summary
	add_skills_summary_button(frm) {
		if (frm.is_new()) return;

		frm.add_custom_button("View Skills Summary", () => {
			const skills = frm.doc.employee_skill || [];

			if (!skills.length) {
				frappe.msgprint("No skills found for this employee.");
				return;
			}

			let rows = skills.map(skill => `
				<tr>
					<td style="padding: 8px; border: 1px solid #ddd;">${skill.skill || ""}</td>
					<td style="padding: 8px; border: 1px solid #ddd;">${skill.proficiency || ""}</td>
					<td style="padding: 8px; border: 1px solid #ddd;">${skill.years_of_experience || 0}</td>
				</tr>
			`).join("");

			const html = `
				<div style="max-height: 400px; overflow-y: auto;">
					<table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
						<thead>
							<tr>
								<th style="padding: 8px; border: 1px solid #ddd;">Skill</th>
								<th style="padding: 8px; border: 1px solid #ddd;">Proficiency</th>
								<th style="padding: 8px; border: 1px solid #ddd;">Experience (Years)</th>
							</tr>
						</thead>
						<tbody>
							${rows}
						</tbody>
					</table>
				</div>
			`;

			const dialog = new frappe.ui.Dialog({
				title: "Employee Skills Summary",
				fields: [
					{
						fieldtype: "HTML",
						fieldname: "skills_summary",
						options: html
					}
				],
				size: "large"
			});

			dialog.show();
		});
	}
});