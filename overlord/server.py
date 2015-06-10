import os, spur, httplib, platform, time
from overlord import celery
from urlparse import urlparse
from datetime import datetime, timedelta

@celery.task
def rebuildWikiPassword():
  shell = spur.SshShell(
    hostname=os.environ['TNYU_Wiki_SERVER_IP'],
    username=os.environ['TNYU_Wiki_SERVER_USER'],
    password=os.environ['TNYU_Wiki_SERVER_PASSWORD'],
    missing_host_key=spur.ssh.MissingHostKey.accept
  )
  with shell:
    result = shell.run(["node", "index.js"], cwd="/root/wiki-service", allow_error=True)
  if result.return_code > 4:
    return False
  return True

def checkUptime(site):
  url = urlparse(site)
  error = ""
  try:
    conn = httplib.HTTPConnection(url[1])
    # Use a HEAD request to get the status code
    conn.request("HEAD", url[2])
    status = conn.getresponse()
    error = status.status
    return True
  except:
    return False

# Restarts services.tnyu.org if it goes down
@celery.task
def monitorServices():
  result = checkUptime(os.environ['TNYU_Services_SERVER_Address'])
  if not result:
    # if services is down we have to restart it
    shell = spur.SshShell(
      hostname=os.environ['TNYU_Services_SERVER_IP'],
      username=os.environ['TNYU_Services_SERVER_USER'],
      password=os.environ['TNYU_Services_SERVER_PASSWORD'],
      missing_host_key=spur.ssh.MissingHostKey.accept
    )
    with shell:
      shell.run(["forever", "stopall"], cwd="/root", allow_error=True)
      shell.run(["forever", "start", "index.js"], cwd="/root/services", allow_error=True)
      shell.run(["forever", "start", "calendar.js"], cwd="/root/calendar-server", allow_error=True)
      result = shell.run(["forever", "start", "index.js"], cwd="/root/proxy", allow_error=True)
    if result.return_code > 4:
      return False
    return True
  return True