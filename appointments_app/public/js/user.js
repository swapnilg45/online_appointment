// Copyright (c) 2024, os and contributors
// For license information, please see license.txt

frappe.ui.form.on("User", {
	refresh(frm) {
        frm.add_custom_button(__('Get User Email Address'), function(){
            frappe.msgprint(frm.doc.email);
        });
	},
});


