from overlord import celery
from datetime import *
from dateutil.parser import parse
from dateutil.relativedelta import *
import os, sendgrid, requests, json, calendar, pytz

sg = sendgrid.SendGridClient(os.environ['TNYU_SendGrid_Username'], os.environ['TNYU_SendGrid_API'])

def sendEmail(emailsTo, subject, body):
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
def unpublishedEventCheck():
  headers = {
    'content-type': 'application/vnd.api+json', 
    'accept': 'application/*, text/*', 
    'x-api-key': os.environ['TNYU_API_KEY']
  }
  draftID = '54837a0ef07bddf3776c79da'
  events = requests.get('https://api.tnyu.org/v2/events?filter[simple][status]=' + draftID, headers=headers, verify=False)
  eventsData = json.loads(events.text)
  today = datetime.now(pytz.UTC)
  for event in eventsData['data']:
    startDateTime = parse(event['attributes']['startDateTime'])
    if startDateTime < today:
      personID = event['links'] and event['links']['addedBy'] and event['links']['addedBy']['linkage'] and event['links']['addedBy']['linkage']['id']
      person = requests.get('https://api.tnyu.org/v2/people/' + personID, headers=headers, verify=False)
      personData = json.loads(person.text)
      personEmail = personData['data'] and personData['data']['attributes'] and personData['data']['attributes']['contact'] and personData['data']['attributes']['contact']['email']
  return True
