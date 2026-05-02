# Employee Hub

Employee Hub is a centralized employee management application built on the [Frappe Framework](https://frappeframework.com). It helps organizations manage employee-related workflows such as onboarding, attendance tracking, leave requests, task assignments, internal approvals, and daily operations through a clean and user-friendly interface.

## Setup Instructions

### Prerequisites

- Python >= 3.14
- Node.js (v24+)
- Redis
- MariaDB 
- [Frappe Bench](https://github.com/frappe/bench) CLI

### Installation

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch version-16
bench install-app employee_hub
bench start
```

The app will be available at `http://localhost:8000`.

## Features

### Employee Management
- **Employee Records** — Store personal details (name, email, phone, DOB, address, profile photo) and professional details (department, designation, reporting manager, date of joining).
- **Auto-generated Full Name** — Full name is automatically computed from first and last name on every save.
- **Employee Status Tracking** — Track employee lifecycle with statuses: Active, On Leave, Inactive, Terminated. A color-coded dashboard indicator is shown on each employee form.
- **Age & Date Validations** — Employees must be at least 18 years old; date of joining cannot be in the future or before date of birth.
- **Email Validation** — Employee email is validated using Frappe's built-in email validator.

### Department & Designation
- **Department Management** — Create and organize departments for grouping employees.
- **Designation Management** — Define job titles linked to departments. Designations are automatically filtered by the selected department on the employee form.

### Skills Management
- **Skill Tracking** — Maintain a master list of skills and assign them to employees with proficiency level and years of experience.
- **Skills Summary Dialog** — View a formatted skills summary table for any employee via a custom button on the employee form.

### Leave Management
- **Leave Requests** — Employees can submit leave requests with leave type (Casual, Sick, Earned, Compensatory), date range, and reason. Total days are auto-calculated.
- **Leave Approval Workflow** — Built-in workflow with Pending → Approved / Rejected / Cancelled states. Leave balance is automatically deducted on submission and restored on rejection or cancellation.
- **Leave Configuration** — Centralized single DocType to configure:
  - Default annual leave balance (auto-assigned to new employees)
  - Per-type limits (max casual, sick, earned leave per request)
  - Maximum leave days per request
  - Toggle for allowing/disallowing backdated leave
- **Self-Service Enforcement** — Non-HR users can only create leave requests for themselves. Employees can only edit their own records.
- **Quick Leave Request** — Create a leave request directly from the employee form via a custom button.

### Reporting
- **Department-Wise Employee Summary** — Script report with bar chart showing per-department breakdown of total employees, active/inactive count, average leave balance, and most common skill (top skill).

### ID Card Printing
- **Employee ID Card** — A custom Jinja print format that generates a styled, printable ID card for any employee, including photo, name, department, designation, and contact details.

### Security & Permissions
- **Role-Based Access** — HR Admin and HR Manager roles have full access; regular employees can view other employees' details but can only edit their own records.
- **Permission Query Conditions** — Leave requests are filtered server-side so employees only see their own requests.
- **Field-Level Permissions** — Employee forms become read-only when a non-admin employee views another employee's record.

### Fixtures & Extensibility
- Exports for Custom Fields, Property Setters, Roles, and the Leave Approval Workflow are included as fixtures for easy deployment across environments.

### Development Setup

```bash
cd apps/employee_hub
pre-commit install
```

Pre-commit is configured with: **ruff**, **eslint**, **prettier**, **pyupgrade**.

## DocType List

| DocType | Description |
|---|---|
| **Employee** | Core employee record with personal and professional details |
| **Department** | Organizational departments for grouping employees |
| **Designation** | Job titles / designations assigned to employees |
| **Skill** | Master list of skills |
| **Employee Skill** | Links skills to individual employees (child table) |
| **Leave Request** | Employee leave applications and approval workflow |
| **Leave Configuration** | Rules and policies for leave allocation |

## Assumptions

- Built for **Frappe v16** (bench version-16 branch).
- Requires a working Frappe Bench environment with Redis, a database, and Node.js already configured.
- Leave management follows a request → approval workflow; leave policies are defined via **Leave Configuration**.
- The app is a standalone Frappe app — it does **not** depend on ERPNext or HR Module.

## License

MIT
