// Copyright (c) 2023, Build With Hussain and contributors
// For license information, please see license.txt

frappe.ui.form.on("Appointment", {
	refresh(frm) {
        if(frm.doc.docstatus===1){
            frm.add_custom_button(__('Reshedule'), function(){
                let d = new frappe.ui.Dialog({
                    title: 'Reshedule Appointment',
                    fields: [
                        {
                            label: 'Date',
                            fieldname: 'date',
                            fieldtype: 'Date'
                        },
                    ],
                    size: 'small', // small, large, extra-large 
                    primary_action_label: 'Reshedule',
                    primary_action(values) {
                        console.log(values);
                        date = values.date

                        frappe.call({
                            method: "appointments_app.appointments_app.doctype.appointment.appointment.validate_reshedule",
                            args:{
                                app_name: frm.doc.name,
                                clinic: frm.doc.clinic,
                                date: date
                            },
                            callback: function (r) {
                                if(r.message){
                                    window.location.reload()
                                }
                                // window.location.reload()
                            },
                        });

                        d.hide();
                    }
                });

                d.show();

            });
        }


        frm.set_query('shift', (doc) => {
            return {
                filters: {
                    "clinic": doc.clinic
                }
            }
        })
	},
});
