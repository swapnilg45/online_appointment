import frappe

from twilio.rest import Client
from frappe.utils.password import get_decrypted_password

def get_twilio_client():
    account_sid = frappe.db.get_single_value("Appointment Twilio Settings", "account_sid")
    auth_token = get_decrypted_password("Appointment Twilio Settings", "Appointment Twilio Settings", "auth_token")

    if not account_sid or not auth_token:
        frappe.throw("Please enter your Twilio Account SID and Auth Token in Appointments Twilio Settings")

    return Client(account_sid, auth_token)



def send_message(body, from_, to_):
    client = get_twilio_client()
    message = client.messages.create(
        body=body,
        from_=from_,
        to=to_
    )

    try:
        frappe.get_doc({
            "doctype": "Appointment SMS Log",
            "twilio_sid": message.sid,
            "body": body,
            "to_": to_,
            "from_": from_,
        }).insert(ignore_permissions=True)
    except Exception:
        frappe.log_error("Appointments SMS Log Creation Failed")
    return message.sid