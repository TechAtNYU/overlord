import os, spur
from subprocess import call
from celery import Celery
from circleclient import circleclient

app = Celery(
  'overlord',
  broker='amqp://guest:guest@localhost//',
  backend='amqp'
)
app.config_from_object('celeryconfig')

token = os.environ['TNYU_CIRCLECI_API_TOKEN']
client = circleclient.CircleClient(token)

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
    call(["git", "add", "."], cwd="/root/backup/")
    call(["git", "commit", "-am", '"Adding Updates"'], cwd="/root/backup/")
    call(["git", "push", "-u", "origin", "master"], cwd="/root/backup/")
    return True
  return False

@app.task
def backupMySQLWithoutHost():
  shell = spur.SshShell(
    hostname=os.environ['TNYU_BD_SERVER_IP'],
    username=os.environ['TNYU_BD_SERVER_USER'],
    password=os.environ['TNYU_BD_SERVER_PASSWORD'],
    missing_host_key=spur.ssh.MissingHostKey.accept
  )
  with shell:
    passwordCombination = "-p" + os.environ['TNYU_BD_MYSQL_PASSWORD']
    shell.run(["mysqldump", "zurmo", "-u", "zurmo", passwordCombination, ">", "/root/backups/sql.sql"], cwd="/root/backups", allow_error=True)
    shell.run(["git", "add", "."], cwd="/root/backups", allow_error=True)
    shell.run(["git", "commit", "-am", '"Adding Updates"'], cwd="/root/backups", allow_error=True)
    result = shell.run(["git", "push", "-u", "origin", "master"], cwd="/root/backups", allow_error=True)
  if result.return_code > 4:
    return False
  return True

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

@app.task
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

if __name__ == '__main__':
  app.start()
