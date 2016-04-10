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


def get_emails(event_id, event_data, eboard_members, attendees):
    res = requests.get('https://api.tnyu.org/v3/events/' + event_id +
                       '?include=attendees', headers=headers, verify=False)

    if res.status_code != 200:
        return

    r = res.json()

    event_data.append(r['data'])

    for post in r['included']:
        if post['attributes'].get('contact'):
            if post['attributes']['roles']:
                eboard_members.append(post)
            else:
                attendees.append(post)


def generate_emails(event_data, survey_link, eboard_members, attendees):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(os.environ['TNYU_EMAIL'], os.environ['TNYU_EMAIL_PASSWORD'])

    for i, member in enumerate(eboard_members):
        msg = "\r\n".join([
            'Hi ' + eboard_members[i]['attributes']['name'] + '!\n\n' +
            'Thanks for coming out! We are constantly looking to improve ' +
            'on our events, and we would really appreciate it if you ' +
            'could take two minutes out of your day to fill out our' +
            'feedback form. We\'d love to know how we could do better: ' +
            survey_link + '?rsvpId=' + eboard_members[i]['id'],
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
            server.sendmail(os.environ['TNYU_EMAIL'], eboard_members[i][
                            'attributes']['contact']['email'], msg)
        except UnicodeEncodeError:
            continue

    for i, attendee in enumerate(attendees):
        msg = "\r\n".join([
            "From: " + os.environ['TNYU_EMAIL'],
            "To: " + attendees[j]['attributes']['contact']['email'],
            "Subject: Thank you for coming to Tech@NYU's " +
            event_data[0]['attributes']['title'],
            '',
            'Hi ' + attendees[j]['attributes']['name'] + '!\n\n' +
            'Thanks for coming out! We are constantly looking to improve ' +
            'on our events, and we would really appreciate it if you could ' +
            ' take two minutes out of your day to fill out our feedback ' +
            'form. We\'d love to know how we could do better: ' +
            survey_link + '?rsvpId=' + attendees[j]['id'],
            '',
            'Filling the form out will give us an idea of how everything ' +
            'went and if there was something you really liked about the ' +
            'event or something you did not like.\n',
            'Feel free to email feedback@techatnyu.org if you have other ' +
            'questions or concerns.',
            '',
            'Thank you,',
            'Tech@NYU team'
        ])

        try:
            server.sendmail(os.environ['TNYU_EMAIL'], attendees[j][
                            'attributes']['contact']['email'], msg)
        except UnicodeEncodeError:
            continue

    server.quit()


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

        if event_date < today:
            break

        if event_date == today:
            today_events.append(event)

    return today_events


@celery.task
def send_emails():
    for event in get_events_ended_today():
        eboard_members = []
        attendees = []
        event_data = []
        survey_link = 'https://techatnyu.typeform.com/to/ElE6F5'
        get_emails(event.id, event_data, eboard_members, attendees)
        generate_emails(event_data, survey_link, eboard_members, attendees)
