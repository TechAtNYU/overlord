import os
import spur
import httplib

from overlord import celery
from urlparse import urlparse

def check_uptime(site):
    """
    Simple script to perform HTTP requests to any URL and see if it
    throws an exception when we do a HEAD request.
    """
    url = urlparse(site)
    try:
        conn = httplib.HTTPConnection(url[1])
        # Use a HEAD request to get the status code
        conn.request("HEAD", url[2])
        return True
    except:
        return False


@celery.task
def monitor_services():
    """
    Does an SSH into the services server and restarts the server if it seems
    that it is down. Useful since it catches most bugs:
    Restarts services.tnyu.org if it goes down.
    """
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


@celery.task
def monitor_techatnyu_org():
    """
    Does an SSH into the API server and restarts the server if it seems that
    it is down. Useful since it catches most bugs:
    # Restarts techatnyu.org if it goes down.
    """
    result = check_uptime(os.environ['TNYU_Org_Website_SERVER_Address'])
    if not result:
        # if services is down we have to restart it
        shell = spur.SshShell(
            hostname=os.environ['TNYU_Org_Website_SERVER_IP'],
            username=os.environ['TNYU_Org_Website_SERVER_USER'],
            private_key_file="/home/api/.ssh/id_rsa",
            missing_host_key=spur.ssh.MissingHostKey.accept,
        )
        with shell:
            shell.run(["forever", "stopall"],
                      cwd="/var/apps/tech-nyu-site", allow_error=True)
            result = shell.run(["forever", "start", "server.js"],
                               cwd="/var/apps/tech-nyu-site/build",
                               allow_error=True)
        if result.return_code > 4:
            return False

    return True
