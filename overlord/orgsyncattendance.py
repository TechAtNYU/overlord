import os
import requests

from datetime import datetime
from dateutil.parser import parse
from pytz import timezone
from datetime import timedelta

from threading import Thread
from overlord import celery
from utils import Event, Email, headers

import StringIO
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import Encoders
from email.MIMEBase import MIMEBase

import smtplib

class OrgSyncAttendance(object):

    def _generate_emails(self, numbers, title):

        msg = MIMEMultipart()
        msg['From'] = os.environ['TNYU_EMAIL']
        msg['To'] = 'server@techatnyu.org'
        msg['Subject'] = 'Attendees for ' + title 

        msg.attach(MIMEText('Attached are the attendees for the event. Please upload to orgsync'))

        output = StringIO.StringIO()
        for num in numbers:
            output.write(num + '\n')

        filename = 'Attendance.csv'

        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(output.getvalue())
        Encoders.encode_base64(attachment)
        attachment.add_header("Content-Disposition", "attachment", filename=filename)
        msg.attach(attachment)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(
            os.environ['TNYU_EMAIL'], os.environ['TNYU_EMAIL_PASSWORD'])
        server.sendmail(os.environ['TNYU_EMAIL'], 'server@techatnyu.org', msg.as_string())
        server.quit()
        output.close()

    def send_emails(self, nNumbers, title):
        self._generate_emails(nNumbers, title)


def get_resource():
    root_url = "https://api.tnyu.org/v3/events/"
    r = requests.get(root_url + "?sort=-endDateTime", headers=headers)
    return r.json()

def get_attendees(eventId):
    root_url = "https://api.tnyu.org/v3/events/"
    r = requests.get(root_url + eventId + "?include=attendees", headers=headers)
    return r.json()['included']


def get_events_ended_recently():
    resources = get_resource()['data']
    events = [Event(x) for x in resources]

    # Change timezone to UTC
    now = timezone("America/New_York").localize(datetime.today())
    recent_events = []

    for event in events:
        event_date = parse(event.endDateTime)
        diff = now - event_date
        if diff <= timedelta(minutes=31) and diff >= timedelta(milliseconds=0):
            recent_events.append(event)

    return recent_events

def get_csvs_for_events(events):
    csvs_for_event = {}
    for event in events:
        attendees = get_attendees(event.id)
        if len(attendees) > 0:
            csvs_for_event[event.id] = []
        for person in attendees:
            att = person['attributes']
            if 'nNumber' in att:
                csvs_for_event[event.id].append(';8' + person['attributes']['nNumber'][1:] + '=1227?')
    return csvs_for_event


@celery.task
def send_emails():
    emails = OrgSyncAttendance()
    events = get_events_ended_recently()
    csvs_for_event = get_csvs_for_events(events)

    for event in events:
        if event.id in csvs_for_event:
            thr = Thread(target=emails.send_emails, args=[csvs_for_event[event.id], event.title])
            thr.start()

    return True