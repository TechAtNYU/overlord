import smtplib
import os
import requests

from datetime import datetime
from dateutil.parser import parse
from overlord import celery

headers = {
    'content-type': 'application/vnd.api+json',
    'accept': 'application/*, text/*',
    'authorization': 'Bearer ' + os.environ['TNYU_API_KEY']
}


class Event(object):

    """
    Class to represent a Tech @ NYU Event
    """

    def __init__(self, json_obj):
        self.id = json_obj['id']
        self._attributes = json_obj['attributes']

    def __getattr__(self, attr):
        if attr not in self._attributes:
            raise AttributeError("Event object has no attribute " + attr)
        return self._attributes[attr]

    def __repr__(self):
        return self.title.encode('utf-8')


class FeedBackEmail(object):

    def __init__(self, survey_link):
        self.survey_link = survey_link

        self.eboard_members = []
        self.attendees = []
        self.event_data = []

        self.server = smtplib.SMTP('smtp.gmail.com', 587)
        self.server.starttls()
        self.server.login(
            os.environ['TNYU_EMAIL'], os.environ['TNYU_EMAIL_PASSWORD'])

    def _get_emails(self, event_id):
        res = requests.get('https://api.tnyu.org/v3/events/' + event_id +
                           '?include=attendees', headers=headers, verify=False)

        if res.status_code != 200:
            return

        r = res.json()

        self.event_data.append(r['data'])

        for post in r['included']:
            if post['attributes'].get('contact'):
                if post['attributes']['roles']:
                    self.eboard_members.append(post)
                else:
                    self.attendees.append(post)

    def _generate_emails(self, members):
        for i, member in enumerate(members):
            msg = "\r\n".join([
                "From: " + os.environ['TNYU_EMAIL'],
                "To: " + members[i]['attributes']['contact']['email'],
                "Subject: Thank you for coming to Tech@NYU's " +
                self.event_data[0]['attributes']['title'],
                '',
                'Hi ' + members[i]['attributes']['name'] + '!\n\n' +
                'Thanks for coming out! We are constantly looking to improve ' +
                'on our events, and we would really appreciate it if you ' +
                'could take two minutes out of your day to fill out our' +
                'feedback form. We\'d love to know how we could do better: ' +
                self.survey_link + '?rsvpId=' + members[i]['id'],
                '',
                'Filling the form out will give us an idea of how everything ' +
                'went and if there was something you really liked about the ' +
                'event or something you did not like.\n',
                'Feel free to email feedback@techatnyu.org if you have ' +
                'other questions or concerns.',
                '',
                'Thank you,',
                'Tech@NYU team'
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

    def __del__(self):
        self.server.quit()


def get_resource():
    root_url = "https://api.tnyu.org/v3/events/"
    r = requests.get(root_url + "?sort=-endDateTime", headers=headers)
    return r.json()


def get_events_ended_today():
    resources = get_resource()['data']
    events = [Event(x) for x in resources]
    today = datetime.today().date()

    today_events = []

    for event in events:
        event_date = parse(event.endDateTime).date()

        # Break the loop if an event in the past is detected
        if event_date < today:
            break

        # Check if an event ended today
        if event_date == today:
            today_events.append(event)

    return today_events


@celery.task
def send_emails():
    survey_link = 'https://techatnyu.typeform.com/to/ElE6F5'
    emails = FeedbackEmail(survey_link)

    for event in get_events_ended_today():
        emails.send_emails(event.id)
