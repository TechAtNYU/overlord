from __future__ import absolute_import
import os
import requests
from os import path, environ
import json
from flask import Flask, Blueprint, abort, jsonify, request, session, render_template
import celeryconfig
from celery import Celery

app = Flask(__name__)
app.config.from_object(celeryconfig)


def make_celery(app):
    celery = Celery(
        'overlord',
        broker='amqp://guest:guest@localhost//',
        backend='amqp',
        include=["backup", "server", "static", "reminder"],
    )
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

# Static


@app.route("/")
def homePage():
    return render_template('index.html')


@app.route("/<userId>/json")
def getJSON(userId):
    headers = {
        'content-type': 'application/vnd.api+json',
        'accept': 'application/*, text/*',
        'x-api-key': os.environ['TNYU_API_KEY']
    }
    person = requests.get('https://api.tnyu.org/v2/people/' +
                          userId, headers=headers, verify=False)
    personData = json.loads(person.text)
    if len(personData['data']['attributes']['roles']) > 0:
        return jsonify({
            'flower': 'http://overlord.tnyu.org:5555/',
            'static': [
                {
                    'name': 'trigger_build',
                    'parameters': ['repository', 'branch'],
                    'path': '/task/static/trigger_build/<repository>/<branch>',
                    'result': '/result/static/trigger_build/<task_id>',
                }
            ],
            'server': [
                {
                    'name': 'monitor_services',
                    'parameters': [],
                    'path': '/task/server/monitor_services',
                    'result': '/result/server/monitor_services/<task_id>',
                },
                {
                    'name': 'monitor_techatnyu_org',
                    'parameters': [],
                    'path': '/task/server/monitor_techatnyu_org',
                    'result': '/result/server/monitor_techatnyu_org/<task_id>',
                }
            ],
            'backup': [
                {
                    'name': 'backup_bd_MySQL',
                    'parameters': [],
                    'path': '/task/backup/backup_bd_MySQL',
                    'result': '/result/backup/backup_bd_MySQL/<task_id>',
                },
                {
                    'name': 'backup_mongo',
                    'parameters': [],
                    'path': '/task/backup/backup_mongo',
                    'result': '/result/backup/backup_mongo/<task_id>',
                },
                {
                    'name': 'backup_jira',
                    'parameters': [],
                    'path': '/task/backup/backup_jira',
                    'result': '/result/backup/backup_jira/<task_id>',
                }
            ]
        })
    # jsonify will do for us all the work, returning the
    # previous data structure in JSON
    return jsonify({'status': '401'})


@app.route("/task/static/<task>/<repository>/<branch>")
def staticWeb(task, repository, branch):
    # Static
    if task == 'trigger_build':
        from static import trigger_build
        res = trigger_build.apply_async([repository, branch])
    context = {"id": res.task_id, "repository": repository, "branch": branch}
    result = "trigger_build({repository}, {branch})".format(
        context['repository'], context['branch'])
    goto = "{}".format(context['id'])
    return jsonify(result=result, goto=goto)


@app.route("/result/static/<task>/<task_id>")
def staticWebResult(task, task_id):
    # Static Result
    if task == 'trigger_build':
        from static import trigger_build
        retval = trigger_build.AsyncResult(task_id).get(timeout=1.0)
        return repr(retval)
    return jsonify({"Error": "Wrong taskID"})


@app.route("/task/server/<task>")
def serverWeb(task):
    # Server
    if task == 'monitor_services':
        from server import monitor_services
        res = monitor_services.apply_async([])
    elif task == 'monitor_techatnyu_org':
        from server import monitor_techatnyu_org
        res = monitor_techatnyu_org.apply_async([])
    context = {"id": res.task_id}
    result = task + "()"
    goto = "{}".format(context['id'])
    return jsonify(result=result, goto=goto)


@app.route("/result/server/<task>/<task_id>")
def serverWebResult(task, task_id):
    # Server Result
    if task == 'monitor_services':
        from server import monitor_services
        retval = monitor_services.AsyncResult(task_id).get(timeout=1.0)
        return repr(retval)
    elif task == 'monitor_techatnyu_org':
        from server import monitor_techatnyu_org
        retval = monitor_techatnyu_org.AsyncResult(
            task_id).get(timeout=1.0)
        return repr(retval)
    return jsonify({"Error": "Wrong taskID"})


@app.route("/task/backup/<task>")
def backupWeb(task):
    # Backup
    if task == 'backup_bd_MySQL':
        from backup import backup_bd_MySQL
        res = backup_bd_MySQL.apply_async([])
        result = "backup_bd_MySQL()"
    elif task == 'backup_mongo':
        from backup import backup_mongo
        res = backup_mongo.apply_async([])
        result = "backup_mongo()"
    elif task == 'backup_jira':
        from backup import backup_jira
        res = backup_jira.apply_async([])
        result = "backup_jira()"
    context = {"id": res.task_id}
    goto = "{}".format(context['id'])
    return jsonify(result=result, goto=goto)


@app.route("/result/backup/<task>/<task_id>")
def backupWebResult(task, task_id):
    # Server Result
    if task == 'backup_bd_MySQL':
        from backup import backup_bd_MySQL
        retval = backup_bd_MySQL.AsyncResult(task_id).get(timeout=1.0)
        return repr(retval)
    elif task == 'backup_mongo':
        from backup import backup_mongo
        retval = backup_mongo.AsyncResult(task_id).get(timeout=1.0)
        return repr(retval)
    elif task == 'backup_jira':
        from backup import backup_jira
        retval = backup_jira.AsyncResult(task_id).get(timeout=1.0)
        return repr(retval)
    return jsonify({"Error": "Wrong taskID"})

celery = make_celery(app)

if __name__ == "__main__":
    port = int(environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
