


import frappe

# appointments_app.appointments_app.doc_events.user.before_save
def before_save(self, method):
    self.middle_name = "Rajesh"