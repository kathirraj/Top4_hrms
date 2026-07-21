// Copyright (c) 2026, Pro Mark and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Monthly Attendance Upload", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Monthly Attendance Upload", {
    refresh(frm) {

        if (frm.is_new()) return;

        let btn = frm.add_custom_button(__('<i class="fa fa-upload"></i> Generate Attendance'), function () {

            frm.call("generate_attendance").then(() => {
                frm.reload_doc();
            });

        });
        btn.css({
            "background": "#28a745",
            "color": "#fff",
            "border": "1px solid #28a745",
            "font-weight": "600"
        });

    },
    from_date(frm) {
        if (!frm.doc.from_date) return;

        frm.set_value(
            "to_date",
            frappe.datetime.add_days(
                frappe.datetime.add_months(frm.doc.from_date, 1),
                -1
            )
        );
    }
});