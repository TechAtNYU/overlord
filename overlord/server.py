import os, spur
from overlord import app

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