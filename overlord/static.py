import os
from circleclient import circleclient
from overlord import celery

token = os.environ['TNYU_CIRCLECI_API_TOKEN']
client = circleclient.CircleClient(token)


@celery.task
def trigger_build(projectName, branchName):
    """
    This task runs our CircleCI builds. If you look at our
    "celeryconfig.py" file you would see that we have
    CircleCI builds that are scheduled for every 15 minutes, etc.
    This basically is responsible for building all of our projects
    and uploading them onto Rackspace Cloud Files in those increments.
    """
    status = client.build.trigger('techatnyu', projectName, branchName)
    if status['failed'] is None:
        return True
    return False
