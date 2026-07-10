// Copyright (c) 2026, Pro Mark and contributors
// For license information, please see license.txt

frappe.query_reports["Payroll report"] = {
	filters: [
    {
      fieldname: "name",
      label: "Employee ID",
      fieldtype: "Link",
      options: "Employee",
    },
    {
      fieldname: "branch",
      label: "Work Location",
      fieldtype: "Link",
      options: "Branch",
    },
    {
      fieldname: "from_date",
      label: "From Date",
      fieldtype: "Date",
      default: get_month_start_date(),
      onchange: function () {
        let from_date = frappe.query_report.get_filter_value("from_date");
        if (from_date) {
          let to_date = get_month_end_date(from_date);
          frappe.query_report.set_filter_value("to_date", to_date);
        } else {
          frappe.query_report.set_filter_value("to_date", "");
        }
      },
    },
    {
      fieldname: "to_date",
      label: "To Date",
      fieldtype: "Date",
      default: get_month_end_date(get_month_start_date()),
    },
  ],
};

function get_month_start_date() {
  let today = frappe.datetime.nowdate();
  let year = parseInt(today.substr(0, 4));
  let month = parseInt(today.substr(5, 2));
  return `${year}-${(month < 10 ? "0" : "") + month}-01`;
}

function get_month_end_date(from_date) {
  let date_obj = new Date(from_date);
  let year = date_obj.getFullYear();
  let month = date_obj.getMonth() + 1; // JavaScript months are 0-based
  let last_day = new Date(year, month, 0).getDate(); // Last day of the month

  let month_str = (month < 10 ? "0" : "") + month;
  return `${year}-${month_str}-${last_day}`;
}