# Copyright (c) 2024, os and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ScheduleShift(Document):
	def before_save(self):
		self.set_title()
	
	def set_title(self):
		self.title = f'{self.start_time}-{self.end_time}'
