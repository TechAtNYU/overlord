import os, httplib, platform, time, sendgrid
from overlord import celery
from urlparse import urlparse
from datetime import datetime, timedelta

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
