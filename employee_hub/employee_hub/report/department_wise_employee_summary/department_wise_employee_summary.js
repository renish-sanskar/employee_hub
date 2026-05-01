frappe.query_reports["Department Wise Employee Summary"] = {
    filters: [
        {
            fieldname: "department",
            label: "Department",
            fieldtype: "Link",
            options: "Department",
            width: 200
        },
        {
            fieldname: "employee_status",
            label: "Employee Status",
            fieldtype: "Select",
            options: "\nActive\nInactive\nTerminated",
            width: 150
        }
    ]
};