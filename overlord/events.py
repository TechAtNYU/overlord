import os, spur, httplib, platform, time
from urlparse import urlparse
from datetime import datetime, timedelta

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
