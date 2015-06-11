import os
from circleclient import circleclient
from overlord import celery

token = os.environ['TNYU_CIRCLECI_API_TOKEN']
client = circleclient.CircleClient(token)

@celery.task
def triggerBuild(projectName, branchName):
  status = client.build.trigger('techatnyu', projectName, branchName)
  if status['failed'] is None:
    return True
  return False
