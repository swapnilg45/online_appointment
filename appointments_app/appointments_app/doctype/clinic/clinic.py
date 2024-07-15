import frappe
from frappe.website.website_generator import WebsiteGenerator

class Clinic(WebsiteGenerator):
    def on_update(self):
        if self.has_value_changed("doctor_in"):
            frappe.publish_realtime(
                "doctor_status_changed", 
                {
                    "updated_status": "IN" if self.doctor_in else "OUT", 
                    "clinic": self.name
                }
            )
