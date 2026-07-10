# # Copyright (c) 2025, Armtech and contributors
# # For license information, please see license.txt
import frappe
from frappe import _
from datetime import date , datetime

def get_salary_components_by_type():
    earnings = frappe.db.sql("""
        SELECT DISTINCT sd.salary_component
        FROM `tabSalary Detail` sd
        LEFT JOIN `tabSalary Component` sc ON sd.salary_component = sc.name
        WHERE sd.parentfield = 'earnings'
        ORDER BY sd.salary_component
    """, as_dict=True)

    deductions = frappe.db.sql("""
        SELECT DISTINCT sd.salary_component
        FROM `tabSalary Detail` sd
        LEFT JOIN `tabSalary Component` sc ON sd.salary_component = sc.name
        WHERE sd.parentfield = 'deductions'
        ORDER BY sd.salary_component
    """, as_dict=True)

    earnings = [comp.salary_component for comp in earnings]
    deductions = [comp.salary_component for comp in deductions]

    return earnings, deductions

def salary_result(filters=None):
    name = filters.get('name') if filters else None
    branch = filters.get('branch') if filters else None
    grade = filters.get('grade') if filters else None
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')

    earnings, deductions = get_salary_components_by_type()
    
    conditions = ["ss.docstatus = 1"]
    if name:
        conditions.append(f"ss.employee = '{name}'")
    if branch:
        conditions.append(f"e.branch = '{branch}'")
    if grade:
        conditions.append(f"e.grade = '{grade}'")
    if from_date and to_date:
        conditions.append(f"ss.posting_date BETWEEN '{from_date}' AND '{to_date}'")

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    
    query = f"""
        SELECT
            ss.name as id,
            ss.employee,
            ss.employee_name,
            e.branch,
            e.grade,
            ss.total_working_days,
            ss.salary_structure,
            ss.rounded_total,
            ss.absent_days,
			e.custom_hmi_id,
            (ss.total_working_days - ss.absent_days) AS present_days,
            ss.bank_account_no,
            ss.gross_pay,
            e.ifsc_code,
            ss.bank_name
        FROM `tabSalary Slip` ss
        LEFT JOIN `tabEmployee` e ON ss.employee = e.employee
        {where_clause}
    """
    
    salary_slips = frappe.db.sql(query, as_dict=True)

    data = []
    for slip in salary_slips:
        components_data = frappe.db.sql("""
            SELECT salary_component, parentfield, amount
            FROM `tabSalary Detail`
            WHERE parent = %s
        """, slip.id, as_dict=True)

        row = slip.copy()
        total_earnings = 0
        total_deductions = 0

        for comp in earnings + deductions:
            row[comp.lower().replace(' ', '_')] = 0.00

        for comp in components_data:
            fieldname = comp.salary_component.lower().replace(' ', '_')
            amount = float(comp.amount or 0)
            
            rounded_amount = round(amount,0)
            row[fieldname] = float(f"{rounded_amount:.2f}") 

            row[fieldname] = rounded_amount

            if comp.parentfield == 'earnings':
                total_earnings += rounded_amount
            else:
                total_deductions += rounded_amount

        row['total_earnings'] = round(total_earnings)
        row['total_deductions'] = round(total_deductions)

        data.append(row)

    return earnings, deductions, data

def get_columns(earnings, deductions):
    columns = [
        # {
        #     "label": "Payroll ID",
        #     "fieldname": "id",
        #     "fieldtype": "Data",
        #     "width": 150,
        #     "align": "center"
        # },
        {
            "label": "Employee Code",
            "fieldname": "employee",
            "fieldtype": "Data",
            "width": 110,
            "align": "center"
        },
        {
            "label": "Employee Name",
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "width": 150,
            "align": "left"
        },
		{
            "label": "HMI ID",
            "fieldname": "custom_hmi_id",
            "fieldtype": "Data",
            "width": 100,
            "align": "left"
        },
        {
            "label": "Work Location",
            "fieldname": "branch",
            "fieldtype": "Data",
            "width": 100,
            "align": "left"
        },
        {
            "label": "Grade",
            "fieldname": "grade",
            "fieldtype": "Data",
            "width": 100,
            "align": "left"
        },
        
        {
            "label": "Present Days",
            "fieldname": "present_days",
            "fieldtype": "Data",
            "width": 100,
            "align": "left"
        },
        {
            "label": "LOP Days",
            "fieldname": "absent_days",
            "fieldtype": "Data",
            "width": 130,
            "align": "right"
        },
        # {
        #    "label": "Salary Structure",
        #     "fieldname": "salary_structure",
        #     "fieldtype": "Data",
        #     "width": 100,
        # }
    ]

    # Earnings components
    for comp in earnings:
        columns.append({
            "label": comp,
            "fieldname": comp.lower().replace(' ', '_'),
            "fieldtype": "Currency",
            "width": 120,
            "align": "right"
        })

    # Total Earnings Column
    columns.append({
        "label": "Total Earnings",
        "fieldname": "total_earnings",
        "fieldtype": "Currency",
        "width": 130,
        "align": "right"
    })

    # Deductions components
    for comp in deductions:
        columns.append({
            "label": comp,
            "fieldname": comp.lower().replace(' ', '_'),
            "fieldtype": "Currency",
            "width": 120,
            "align": "right"
        })

    # Total Deductions Column
    columns.append({
        "label": "Total Deductions",
        "fieldname": "total_deductions",
        "fieldtype": "Currency",
        "width": 130,
        "align": "right"
    })
    columns.append({
        "label": "Gross Pay",
        "fieldname": "gross_pay",
        "fieldtype": "Currency",
        "width": 130,
        "align": "right"
    })
    # Net Pay Column
    columns.append({
        "label": "Net Pay",
        "fieldname": "rounded_total",
        "fieldtype": "Currency",
        "width": 130,
        "align": "right"
    })
    columns.append({
        "label": "Bank Name",
        "fieldname": "bank_name",
        "fieldtype": "Data",
        "width": 130,
        "align": "left"
    })
    columns.append({
        "label": "Bank Account No",
        "fieldname": "bank_account_no",
        "fieldtype": "Data",
        "width": 130,
        "align": "right"
    })
    
    columns.append({
        "label": "IFSC Code",
        "fieldname": "ifsc_code",
        "fieldtype": "Data",
        "width": 130,
        "align": "right"
    })
   
    return columns

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def get_month_display_short(from_date, to_date):
    if not from_date or not to_date:
        return "N/A"

    start = datetime.strptime(from_date, '%Y-%m-%d')
    end = datetime.strptime(to_date, '%Y-%m-%d')

    months = []
    current = start.replace(day=1)

    while current <= end:
        month_str = current.strftime('%b')
        months.append(month_str)
        current += relativedelta(months=1)

    # Remove duplicates and sort months
    months = sorted(set(months), key=lambda m: datetime.strptime(m, '%b').month)

    return f"{', '.join(months)} - {start.year}"

def get_current_fy_dates():
    today = date.today()
    year = today.year

    if today.month >= 4:
       
        fy_start_date = date(year, 4, 1)
        fy_end_date = date(year + 1, 3, 31)
    else:
       
        fy_start_date = date(year - 1, 4, 1)
        fy_end_date = date(year, 3, 31)

    return fy_start_date.strftime('%Y-%m-%d'), fy_end_date.strftime('%Y-%m-%d')

def execute(filters=None):
    if not filters.get('from_date') or not filters.get('to_date'):
        filters['from_date'], filters['to_date'] = get_current_fy_dates()

    earnings, deductions, data = salary_result(filters)
    columns = get_columns(earnings, deductions)
    get_current_employee = frappe.db.count('Employee', filters={'status': 'Active'})

    from_date = filters.get('from_date')
    to_date = filters.get('to_date')

    month_display = get_month_display_short(filters.get('from_date'), filters.get('to_date'))

    # Calculate Financial Year
    from_year = int(from_date[:4])
    from_month = int(from_date[5:7])
    if from_month >= 4:
        fy_start_year = from_year
        fy_end_year = from_year + 1
    else:
        fy_start_year = from_year - 1
        fy_end_year = from_year

    fy_display = f"FY {fy_start_year}-{str(fy_end_year)[-2:]}"  # e.g., "FY 2024-25"

    report_summary = [
        {
            "label": _("Month"),
            "value": month_display,
            "indicator": "Red",
            "bgcolor": "#f0f8ff",
        },
        {
            "label": _("Financial Year"),
            "value": fy_display,
            "width": 500,
            "indicator": "Green",
            "bgcolor": "#f0f8ff",
        }
    ]

    return columns, data, None, None, report_summary


