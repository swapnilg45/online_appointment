# Copyright (c) 2023, Build With Hussain and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta


class Appointment(Document):
	def validate(self):
		# validate the contact_number to be a valid 10 digit phone number except the country code,
		# if it does not have a country code, prepend +91
		if not self.contact_number:
			frappe.throw("Please enter a valid contact number")
		if len(self.contact_number) == 10:
			self.contact_number = f"+91{self.contact_number}"
		elif len(self.contact_number) == 13 and self.contact_number.startswith("+91"):
			pass
		else:
			frappe.throw("Please enter a valid contact number")
		validate_appointment(self)
		
	def on_update_after_submit(self):
		validate_appointment(self)

	def after_insert(self):
		self.queue_number = self.add_to_appointment_queue()
		# attach csrf token + queue number as key and queue number as value
		frappe.cache.set_value(f"{frappe.session.sid}:queue_number", self.queue_number)
		self.save(ignore_permissions=True)
		self.send_confirmation_message()

	def add_to_appointment_queue(self):
		filters = {
			"date": self.date,
			"shift": self.shift,
			"clinic": self.clinic,
		}
		appointment_queue_exists = frappe.db.exists(
			"Appointment Queue",
			filters,
		)

		if appointment_queue_exists:
			q = frappe.get_doc("Appointment Queue", filters)
		else:
			q = frappe.new_doc("Appointment Queue")
			q.update(filters)
			q.save(ignore_permissions=True)

		q.append("queue", {"appointment": self.name, "status": "Pending"})
		q.save(ignore_permissions=True)

		return len(q.queue)

	def send_confirmation_message(self):
		shift_title = frappe.db.get_value("Schedule Shift", self.shift, "title")
		message = f"Hi {self.patient_name}, your appointment for {self.clinic} on {self.date} ({shift_title}) has been booked. Your queue number is {self.queue_number}."

		frappe.enqueue(
			"appointments_app.utils.send_message",
			body=message,
			from_=frappe.db.get_single_value(
				"Appointments Twilio Settings", "from_phone_number"
			),
			to=self.contact_number,
		)


def validate_appointment(self):
	appointment_date = datetime.strptime(self.date, '%Y-%m-%d').date()
	min_allowed_date = appointment_date - timedelta(days=3)
	max_allowed_date = appointment_date + timedelta(days=3)

	if frappe.db.exists(
		"Appointment",{
			'patient_name': self.patient_name,
			"date":["between", [min_allowed_date, max_allowed_date]],
			"name":['!=', self.name] if self.name else None
		}
	):
		frappe.throw(f"Patient cannot have apointment 3 days before or after")

@frappe.whitelist()
def validate_reshedule(app_name, clinic, date):
	queue_doc = frappe.db.get_value("Appointment Queue", {
		"date": date,
		"clinic": clinic
	})
	frappe.logger("utils").exception(queue_doc)
	if queue_doc:
		queue_count = frappe.db.get_list("Appointment Queue Item", {"parent": queue_doc})
		if len(queue_count) >= 4:
			frappe.throw("Queue Is Full")
	app_doc = frappe.get_doc("Appointment", app_name)
	app_doc.date = date
	app_doc.queue_number = app_doc.add_to_appointment_queue()
	app_doc.save(ignore_permissions=True)
	return True