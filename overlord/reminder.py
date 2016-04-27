import os
import requests

from datetime import datetime
from dateutil.parser import parse
from dateutil import tz
from pytz import timezone

from threading import Thread
from overlord import celery
from utils import Event, Email, headers


class ReminderEmail(Email):

    def _get_time(self):
        """
        Changes UTC time fetched from the API to New York Time
        """
        date_time = self.event_data[0]['attributes']['startDateTime']
        time = parse(date_time).replace(tzinfo=tz.gettz('UTC'))
        central_time = time.astimezone(tz.gettz('America/New_York'))
        return ":".join(str(central_time.time()).split(":")[0:2])

    def _venue_address(self):
        venue_id = self.event_data[0]['relationships'][
            'venue']['data']['id']
        venue = requests.get(
            "https://api.tnyu.org/v3/venues/" + venue_id, headers=headers)
        address = venue.json()['data']['attributes']['address']
        address_str = "\n".join(address.split(","))
        return address_str

    def _generate_emails(self, members):
        address = self._venue_address()
        time = self._get_time()

        for i, member in enumerate(members):
            msg = "\r\n".join([
                "From: " + os.environ['TNYU_EMAIL'],
                "To: " + members[i]['attributes']['contact']['email'],
                "Subject: Confirmation for Tech@NYU's " +
                self.event_data[0]['attributes']['title'],
                '',
                'Hi ' + members[i]['attributes']['name'] + '!\n\n' +
                "This is your confirmation for the Tech@NYU " +
                self.event_data[0]['attributes']['title'] + " tomorrow at " +
                time + " .The event will be held at: \n\n" + address +
                "\n\nWe look forward to seeing you! Feel free to reach out" +
                " to us if you have any other questions. For more updates" +
                " feel free to follow us on Twitter or Facebook. \n\n" +
                "Thank you",
                "Tech@NYU team"
            ])

            try:
                self.server.sendmail(os.environ['TNYU_EMAIL'], members[i][
                    'attributes']['contact']['email'], msg)
            except UnicodeEncodeError:
                continue

    def send_emails(self, event_id):
        self._get_emails(event_id)
        self._generate_emails(self.eboard_members)
        self._generate_emails(self.attendees)


def get_resource(sort=None):
    root_url = "https://api.tnyu.org/v3/events/"
    r = requests.get(root_url + "?sort=-" + sort, headers=headers)
    return r.json()


def get_events_in_future():
    resources = get_resource(sort="startDateTime")['data']
    events = [Event(x) for x in resources]
    # Change UTC to New York Time
    today = timezone("America/New_York").localize(datetime.today()).date()
    future_events = []

    for event in events:
        event_date = parse(event.startDateTime).date()
        # Check if the event is tomorrow
        if abs(event_date - today).days == 1:
            future_events.append(event)

    return future_events


@celery.task
def send_emails():
    emails = ReminderEmail()
    events = get_events_in_future()
    for event in events:
        thr = Thread(target=emails.send_emails, args=[event.id])
        thr.start()

    return True
