import frappe
from frappe.model.document import Document


class Appointment(Document):
    def after_insert(self):
        queue_number = self.add_to_appointment_queue()
        print('Your queue number is', queue_number)

    def add_to_appointment_queue(self):
        # Try to fetch an existing Appointment Queue document
        queue_name = frappe.db.exists("Appointment Queue", {
            "date": self.date,
            "shift": self.shift,
            "clinic": self.clinic
        })

        if queue_name:
            q = frappe.get_doc("Appointment Queue", queue_name)
        else:
            q = frappe.get_doc({
                "doctype": "Appointment Queue",
                "date": self.date,
                "shift": self.shift,
                "clinic": self.clinic,
            })

        # Append the appointment to the queue
        q.append('queue', {
            'appointment': self.name,
            'status': 'Pending'
        })
        q.save(ignore_permissions=True)

        return len(q.queue)
