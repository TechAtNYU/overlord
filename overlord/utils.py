import smtplib
import requests
import os

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


class Email(object):
    def __init__(self):

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

    def __del__(self):
        self.server.quit()
