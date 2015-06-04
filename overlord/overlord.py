import os, spur
from subprocess import call
from celery import Celery
from celery.schedules import crontab
from circleclient import circleclient

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
  CELERYBEAT_SCHEDULE = {
    'every-day-api': {
        'task': 'overlord.backupMongo',
        'schedule': crontab(minute=0, hour=0),
        'args': (),
    },
    'every-day-wiki': {
        'task': 'overlord.backupMySQLWithHost',
        'schedule': crontab(minute=0, hour=1),
        'args': (),
    },
    'every-hour-intranet': {
        'task': 'overlord.triggerBuild',
        'schedule': crontab(minute='*/45'),
        'args': ('intranet', 'master'),
    },
  }
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
  sqlResult = call(["mysqldump", "wiki"], universal_newlines=True, stdout=sqlFile)
  if sqlResult == 0:
    return True
  return False

@app.task
def backupMongo():
  shell = spur.SshShell(
    hostname=os.environ['TNYU_API_SERVER_IP'],
    username=os.environ['TNYU_API_SERVER_USER'],
    password=os.environ['TNYU_API_SERVER_PASSWORD'],
    missing_host_key=spur.ssh.MissingHostKey.accept
  )
  with shell:
    shell.run(["rm", "-rf", "dump"], cwd="/backup", allow_error=True)
    shell.run(["mkdir", "dump"], cwd="/backup", allow_error=True)
    shell.run(["mongodump", "-h", "localhost", "-o", "dump", "-d", "platform"], cwd="/backup", allow_error=True)
    shell.run(["git", "add", "."], cwd="/backup", allow_error=True)
    shell.run(["git", "commit", "-am", '"Adding Updates"'], cwd="/backup", allow_error=True)
    result = shell.run(["git", "push", "-u", "origin", "master"], cwd="/backup", allow_error=True)
  if result.return_code > 4:
    return False
  return True

if __name__ == '__main__':
  app.start()
