import spur
import os
from subprocess import call
from overlord import celery


@celery.task
def backup_mongo():
    """
    This task runs the MongoDB backup on our API server.
    Then it commits the result to the "api-db-backups"
    repository on Github.
    """
    shell = spur.SshShell(
        hostname=os.environ['TNYU_API_SERVER_IP'],
        username=os.environ['TNYU_API_SERVER_USER'],
        private_key_file="/home/api/.ssh/id_rsa",
        missing_host_key=spur.ssh.MissingHostKey.accept,
    )
    with shell:
        api_dir = "/backup/api-db-backups"
        shell.run(["rm", "-rf", "dump"], cwd=api_dir, allow_error=True)
        shell.run(["mkdir", "dump"], cwd=api_dir, allow_error=True)
        shell.run(["mongodump", "-h", "localhost", "-o", "dump", "-u",
                   os.environ['TNYU_API_MONGO_USER'],
                   '-p', os.environ['TNYU_API_MONGO_PW']],
                  cwd=api_dir, allow_error=True)
        shell.run(["git", "add", "."], cwd=api_dir, allow_error=True)
        shell.run(["git", "commit", "-am", '"Adding Updates"'],
                  cwd=api_dir, allow_error=True)
        result = shell.run(["git", "push", "-u", "origin",
                            "master"], cwd=api_dir, allow_error=True)
    if result.return_code > 4:
        return False
    return True


@celery.task
def backup_jira():
    """
    This task runs the Jira backup on our Jira server.
    Then it commits the result to the "jira-db-backups"
    repository on Github.
    """
    shell = spur.SshShell(
        hostname=os.environ['TNYU_Jira_SERVER_IP'],
        username=os.environ['TNYU_Jira_SERVER_USER'],
        password=os.environ['TNYU_Jira_SERVER_PASSWORD'],
        missing_host_key=spur.ssh.MissingHostKey.accept,
    )
    with shell:
        atlassian_dir = "/var/atlassian/application-data/jira/export"
        shell.run(["git", "add", "."],
                  cwd=atlassian_dir,
                  allow_error=True)
        shell.run(["git", "commit", "-am", '"Adding Updates"'],
                  cwd=atlassian_dir,
                  allow_error=True)
        result = shell.run(["git", "push", "-u", "origin", "master"],
                           cwd=atlassian_dir,
                           allow_error=True)
    if result.return_code > 4:
        return False
    return True


@celery.task
def backup_discuss():
    """
    This task runs the Discuss backup on our Discuss server.
    Then it commits the result to the "discuss-db-backups"
    repository on Github.
    """
    shell = spur.SshShell(
        hostname=os.environ['TNYU_DISCUSS_SERVER_IP'],
        username=os.environ['TNYU_DISCUSS_SERVER_USER'],
        private_key_file="/home/api/.ssh/id_rsa",
        missing_host_key=spur.ssh.MissingHostKey.accept,
    )
    with shell:
        discourse_dir = "/var/discourse/shared/standalone/backups/default"
        shell.run(["git", "add", "."],
                  cwd=discourse_dir,
                  allow_error=True)
        shell.run(["git", "commit", "-am", '"Adding Updates"'],
                  cwd=discourse_dir,
                  allow_error=True)
        result = shell.run(["git", "push", "-u", "origin", "master"],
                           cwd=discourse_dir,
                           allow_error=True)
    if result.return_code > 4:
        return False
    return True
