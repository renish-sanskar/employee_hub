app_name = "employee_hub"
app_title = "Employee Hub"
app_publisher = "Renish Ponkiya"
app_description = "Employee Hub is a centralized employee management application developed using the Frappe Framework. It helps organizations manage employee-related workflows such as employee onboarding, attendance tracking, leave requests, task assignments, internal approvals, and daily operations through a clean and user-friendly interface."
app_email = "ponkiyarenish@gmail.com"
app_license = "mit"

# Apps
# ------------------

# Includes in <head>
app_include_css = "/assets/employee_hub/css/employee_hub.css"
app_include_js = "/assets/employee_hub/js/employee_hub.js"


# Document Events
doc_events = {
    "Employee": {
        "before_save": "employee_hub.employee_hub.doctype.employee.employee.set_full_name"
    }
}


fixtures = [
    "Custom Field",
    "Property Setter",
    "Role",
    {
        "dt": "Workflow",
        "filters": [["name", "=", "Leave Approval Workflow"]]
    }
]

permission_query_conditions = {
    "Leave Request": "employee_hub.employee_hub.doctype.leave_request.leave_request.get_permission_query_conditions",
}