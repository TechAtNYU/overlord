from overlord import celery
from datetime import *
from dateutil.parser import parse
from dateutil.relativedelta import *
import os
import sendgrid
import requests
import json
import calendar
import pytz

sg = sendgrid.SendGridClient(
    os.environ['TNYU_SendGrid_Username'], os.environ['TNYU_SendGrid_API'])


def send_email(emailsTo, subject, body, is_html=False):
    message = sendgrid.Mail()
    if isinstance(emailsTo, list):
        for email in emailsTo:
            if isinstance(email, list):
                message.add_to(email)
    elif isinstance(emailsTo, str):
        message.add_to(emailsTo)
    else:
        return False
    message.set_subject(subject)

    if is_html:
        message.set_html(body)
    else:
        message.set_text(body)

    message.set_from('hello@techatnyu.org')
    try:
        x = sg.send(message)
        if x[0] == 200:
            return True
        else:
            return False
    except SendGridError:
        return False

# Get an update on the event status.
# Unpublished and already passed date
# Incomplete


@celery.task
def unpublished_event_check():
    headers = {
        'content-type': 'application/vnd.api+json',
        'accept': 'application/*, text/*',
        'x-api-key': os.environ['TNYU_API_KEY']
    }
    draft_id = '54837a0ef07bddf3776c79da'
    events = requests.get(
        'https://api.tnyu.org/v2/events?filter[simple][status]=' + draft_id, headers=headers, verify=False)
    events_data = json.loads(events.text)
    today = datetime.now(pytz.UTC)
    for event in events_data['data']:
        start_date_time = parse(event['attributes']['startDateTime'])
        if start_date_time < today:
            person_ID = event['links'] and event['links']['addedBy'] and event['links'][
                'addedBy']['linkage'] and event['links']['addedBy']['linkage']['id']
            person = requests.get(
                'https://api.tnyu.org/v2/people/' + person_ID, headers=headers, verify=False)
            person_data = json.loads(person.text)
            person_email = person_data['data'] and person_data['data']['attributes'] and person_data[
                'data']['attributes']['contact'] and person_data['data']['attributes']['contact']['email']
    return True
