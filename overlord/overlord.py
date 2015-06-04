import os
import shlex
from subprocess import call
from celery import Celery
from circleclient import circleclient
import spur

app = Celery(
  'overlord',
  broker='amqp://guest:guest@localhost//',
  backend='amqp'
)

token = os.environ['TNYU_CIRCLECI_API_TOKEN']
client = circleclient.CircleClient(token)

app.conf.update(
  CELERY_TASK_SERIALIZER='json',
  CELERY_ACCEPT_CONTENT=['json'],
  CELERY_RESULT_SERIALIZER='json',
  CELERY_ENABLE_UTC=True,
  CELERY_TIMEZONE='America/New_York',
)

@app.task
def triggerBuild(projectName, branchName):
  status = client.build.trigger('techatnyu', projectName, branchName)
  if status['failed'] is None:
    return True
  return False

@app.task
def backupMySQLWithHost():
  sqlFile = open('/root/backup/sql.sql', 'wb')
  sqlCmd = "mysqldump wiki"
  sqlResult = call(shlex.split(sqlCmd), universal_newlines=True, stdout=sqlFile)
  if sqlResult == 0:
    return True
  return False

@app.task
def backupMongo():
  SSH_KEY_PATH = '/Users/abhiagarwal/.ssh/id_rsa'
  shell = spur.SshShell(
    hostname="23.253.204.159",
    username="ethan",
    private_key_file=SSH_KEY_PATH
  )
  with shell:
    result = shell.run(["cd", "/backup/"])

  return result.output

if __name__ == '__main__':
  app.start()
