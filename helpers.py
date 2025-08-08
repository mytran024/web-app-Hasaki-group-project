import datetime
import gspread
import os
from oauth2client import service_account

from .models import Appointment, Service, Employee, Feedback, Customer


def get_appointment(year, month, day):
    appointments = Appointment.objects.all().values()

    times = []
    start = 9.0
    end = 21.0
    while start <= end:
        times.append(start)
        start = start + 0.25

    data = dict()
    for t in times:
        hour = int(t)
        minute = int((t - hour) * 60)
        key = datetime.time(hour=hour, minute=minute).strftime("%H:%M")
        data[key] = []
        for appointment in appointments:
            if appointment['start_time'].hour == hour and \
                    appointment['start_time'].minute == minute and \
                    appointment['appointment_date'].year == year and \
                    appointment['appointment_date'].month == month and \
                    appointment['appointment_date'].day == day:
                customer = Customer.objects.get(customer_id=appointment['customer_id'])
                appointment_data = {
                    "appointment_info": appointment,
                    "customer_info": customer
                }
                data[key].append(appointment_data)
    return data


def read_data(sheet_name: str):
    # Define the scope for the API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    script_dir = os.path.dirname(os.path.realpath(__file__))
    authen_path = script_dir.replace("\\", "/").split("/SpaHasaki")[0] + "/static/resources/spahasaki-bbf24db11c1e.json"

    # Provide the path to the downloaded JSON credentials file
    creds = service_account.from_json_keyfile_name(authen_path, scope)

    # Authenticate the client
    client = gspread.authorize(creds)
    sheet = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/1-GgT7TVLd8JL20tiDTSgn74CZUdH1wqJaf_-PMikJLU/edit?usp=sharing").worksheet(
        sheet_name)
    data = sheet.get_all_records()
    return data