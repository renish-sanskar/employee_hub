# Copyright (c) 2026, Renish Ponkiya and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    filters = filters or {}

    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)

    return columns, data, None, chart


def get_columns():
    return [
        {
            "label": "Department",
            "fieldname": "department",
            "fieldtype": "Link",
            "options": "Department",
            "width": 180,
        },
        {
            "label": "Total Employees",
            "fieldname": "total_employees",
            "fieldtype": "Int",
            "width": 140,
        },
        {
            "label": "Active Employees",
            "fieldname": "active_employees",
            "fieldtype": "Int",
            "width": 170,
        },
        {
            "label": "Inactive / Terminated",
            "fieldname": "inactive_employees",
            "fieldtype": "Int",
            "width": 170,
        },
        {
            "label": "Avg Leave Balance",
            "fieldname": "avg_leave_balance",
            "fieldtype": "Float",
            "width": 160,
            "precision": 2,
        },
        {
            "label": "Top Skill",
            "fieldname": "top_skill",
            "fieldtype": "Data",
            "width": 180,
        },
    ]


def get_data(filters):
    conditions = []
    values = {}

    if filters.get("department"):
        conditions.append("e.department = %(department)s")
        values["department"] = filters.get("department")

    if filters.get("employee_status"):
        conditions.append("e.employee_status = %(employee_status)s")
        values["employee_status"] = filters.get("employee_status")

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    data = frappe.db.sql(
        f"""
        SELECT
            e.department AS department,
            COUNT(e.name) AS total_employees,
            SUM(CASE WHEN e.employee_status = 'Active' THEN 1 ELSE 0 END) AS active_employees,
            SUM(CASE WHEN e.employee_status IN ('Inactive', 'Terminated') THEN 1 ELSE 0 END) AS inactive_employees,
            ROUND(AVG(COALESCE(e.annual_leave_balance, 0)), 2) AS avg_leave_balance,
            (
                SELECT es.skill
                FROM `tabEmployee Skill` es
                INNER JOIN `tabEmployee` e2 ON e2.name = es.parent
                WHERE e2.department = e.department
                GROUP BY es.skill
                ORDER BY COUNT(es.skill) DESC
                LIMIT 1
            ) AS top_skill
        FROM `tabEmployee` e
        {where_clause}
        GROUP BY e.department
        ORDER BY e.department
        """,
        values=values,
        as_dict=True,
    )

    return data


def get_chart(data):
    labels = [row.department for row in data]
    values = [row.total_employees for row in data]

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "Employees",
                    "values": values,
                }
            ],
        },
        "type": "bar",
        "height": 300,
        "colors": ["#2563eb"],
    }