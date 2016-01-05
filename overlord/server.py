import os
import spur
import httplib
import platform
import time
from overlord import celery
from urlparse import urlparse
from datetime import datetime, timedelta


def check_uptime(site):
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


@celery.task
def monitor_services():
    # Restarts services.tnyu.org if it goes down
    result = check_uptime(os.environ['TNYU_Services_SERVER_Address'])
    if not result:
        # if services is down we have to restart it
        shell = spur.SshShell(
            hostname=os.environ['TNYU_Services_SERVER_IP'],
            username=os.environ['TNYU_Services_SERVER_USER'],
            password=os.environ['TNYU_Services_SERVER_PASSWORD'],
            missing_host_key=spur.ssh.MissingHostKey.accept,
        )
        with shell:
            shell.run(["forever", "stopall"], cwd="/root", allow_error=True)
            shell.run(["forever", "start", "index.js"],
                      cwd="/root/services", allow_error=True)
            shell.run(["forever", "start", "calendar.js"],
                      cwd="/root/calendar-server", allow_error=True)
            result = shell.run(["forever", "start", "index.js"],
                               cwd="/root/proxy", allow_error=True)
        if result.return_code > 4:
            return False
        return True
    return True


@celery.task
def monitor_techatnyu_org():
    # Restarts techatnyu.org if it goes down
    result = check_uptime(os.environ['TNYU_Org_Website_SERVER_Address'])
    if not result:
        # if services is down we have to restart it
        shell = spur.SshShell(
            hostname=os.environ['TNYU_Org_Website_SERVER_IP'],
            username=os.environ['TNYU_Org_Website_SERVER_USER'],
            password=os.environ['TNYU_Org_Website_SERVER_PASSWORD'],
            missing_host_key=spur.ssh.MissingHostKey.accept,
        )
        with shell:
            shell.run(["forever", "stopall"],
                      cwd="/var/apps/tech-nyu-site", allow_error=True)
            result = shell.run(["forever", "start", "server.js"],
                               cwd="/var/apps/tech-nyu-site/build", allow_error=True)
        if result.return_code > 4:
            return False
        return True
    return True
