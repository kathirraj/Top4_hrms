# Copyright (c) 2026, Pro Mark and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_days, cint


class MonthlyAttendanceUpload(Document):

    @frappe.whitelist()
    def generate_attendance(self):

        if not self.from_date or not self.to_date:
            frappe.throw("Please select From Date and To Date.")

        total_created = 0
        total_skipped = 0

        for row in self.attendance_detail:

            if not row.employee:
                continue

            absent_days = cint(row.absent_days)

            if absent_days <= 0:
                continue

            employee = frappe.get_doc("Employee", row.employee)

            holiday_list = employee.holiday_list

            if not holiday_list:
                holiday_list = frappe.db.get_value(
                    "Company",
                    self.company,
                    "default_holiday_list"
                )

            current_date = getdate(self.from_date)

            while current_date <= getdate(self.to_date):

                if absent_days == 0:
                    break

                # -----------------------------------
                # Skip Holiday
                # -----------------------------------
                if holiday_list:

                    holiday = frappe.db.exists(
                        "Holiday",
                        {
                            "parent": holiday_list,
                            "holiday_date": current_date
                        }
                    )

                    if holiday:
                        current_date = add_days(current_date, 1)
                        continue

                # -----------------------------------
                # Skip Approved Leave
                # -----------------------------------
                leave = frappe.db.sql("""
                    SELECT name
                    FROM `tabLeave Application`
                    WHERE employee=%s
                    AND status='Approved'
                    AND %s BETWEEN from_date AND to_date
                    LIMIT 1
                """, (row.employee, current_date))

                if leave:
                    current_date = add_days(current_date, 1)
                    continue

                # -----------------------------------
                # Skip Existing Attendance
                # -----------------------------------
                attendance = frappe.db.exists(
                    "Attendance",
                    {
                        "employee": row.employee,
                        "attendance_date": current_date
                    }
                )

                if attendance:
                    current_date = add_days(current_date, 1)
                    total_skipped += 1
                    continue

                # -----------------------------------
                # Create Attendance
                # -----------------------------------
                attendance = frappe.get_doc({
                    "doctype": "Attendance",
                    "employee": row.employee,
                    "company": self.company,
                    "attendance_date": current_date,
                    "status": "Absent"
                })

                attendance.insert(ignore_permissions=True)
                attendance.submit()
                total_created += 1
                absent_days -= 1

                current_date = add_days(current_date, 1)

        frappe.db.commit()

        self.db_set("total_employees", len(self.attendance_detail))
        self.db_set("attendance_created", total_created)
        self.db_set("skipped", total_skipped)

        frappe.msgprint(
            f"""
            <b>Attendance Generation Completed</b><br><br>

            Employees : {len(self.attendance_detail)}<br>
            Attendance Created : {total_created}<br>
            Skipped : {total_skipped}
            """
        )