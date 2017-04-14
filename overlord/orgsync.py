import requests
import json
import sys
from datetime import datetime
from dateutil.parser import parse
from pytz import timezone
from utils import headers, Event
from Naked.toolshed.shell import execute_js, muterun_js

from overlord import celery

def get_resource():
    root_url = "https://api.tnyu.org/v3/events/"
    r = requests.get(root_url + "?sort=-endDateTime", headers=headers)
    return r.json()


def get_events_ended_today():
    resources = get_resource()['data']
    events = [Event(x) for x in resources]

    # Change timezone to UTC
    today = timezone("America/New_York").localize(datetime.today()).date()
    today_events = []

    for event in events:
        event_date = parse(event.endDateTime).date()

        # Break the loop if an event in the past is detected
        if event_date < today:
            break

        # Check if an event ended today
        if event_date == today:
            today_events.append(event.raw_json)

    return today_events

# Double encode the JSON string
events_json = json.dumps(get_events_ended_today())
response = muterun_js('orgsync.js', json.dumps(events_json))

@celery.task
def update_orgsync():
    # TODO: Call's Andrew's JS script here
    if response.exitcode == 0:
      print(response.stdout)
    else:
      sys.stderr.write(response.stderr)

