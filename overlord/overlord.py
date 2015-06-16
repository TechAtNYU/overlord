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
    person = requests.get('https://api.tnyu.org/v2/people/' + userId, headers=headers, verify=False)
    personData = json.loads(person.text)
    if len(personData['data']['attributes']['roles']) > 0:
        return jsonify({
            'static': [
            {
                'name': 'triggerBuild',
                'parameters': ['repository', 'branch'],
                'path': '/task/server/triggerBuild/<repository>/<branch>',
                'result': '/result/backup/triggerBuild/<task_id>',
            }
            ],
            'server': [
            {
                'name': 'rebuildWikiPassword',
                'parameters': [],
                'path': '/task/server/rebuildWikiPassword',
                'result': '/result/server/rebuildWikiPassword/<task_id>',
            },
            {
                'name': 'monitorServices',
                'parameters': [],
                'path': '/task/server/monitorServices',
                'result': '/result/server/monitorServices/<task_id>',
            },
            {
                'name': 'monitorTechatNYUOrgWebsite',
                'parameters': [],
                'path': '/task/server/monitorTechatNYUOrgWebsite',
                'result': '/result/server/monitorTechatNYUOrgWebsite/<task_id>',
            },
            {
                'name': 'monitorCheckinWebsite',
                'parameters': [],
                'path': '/task/server/monitorCheckinWebsite',
                'result': '/result/server/monitorCheckinWebsite/<task_id>',
            }
            ],
            'backup': [
            {
                'name': 'backupMySQLWithHost',
                'parameters': [],
                'path': '/task/backup/backupMySQLWithHost',
                'result': '/result/backup/backupMySQLWithHost/<task_id>',
            },
            {
                'name': 'backupMySQLWithoutHost',
                'parameters': [],
                'path': '/task/backup/backupMySQLWithoutHost',
                'result': '/result/backup/backupMySQLWithoutHost/<task_id>',
            },
            {
                'name': 'backupMongo',
                'parameters': [],
                'path': '/task/backup/backupMongo',
                'result': '/result/backup/backupMongo/<task_id>',
            }
            ]
        })
    # jsonify will do for us all the work, returning the
    # previous data structure in JSON
    return jsonify({'status': '401'})

# Static
@app.route("/task/static/<task>/<repository>/<branch>")
def staticWeb(task, repository, branch):
    if task == 'triggerBuild':
        from static import triggerBuild
        res = triggerBuild.apply_async([repository, branch])
    context = {"id": res.task_id, "repository": repository, "branch": branch}
    result = "triggerBuild({repository}, {branch})".format(context['repository'], context['branch'])
    goto = "{}".format(context['id'])
    return jsonify(result=result, goto=goto)

# Static Result
@app.route("/result/static/<task>/<task_id>")
def staticWebResult(task, task_id):
    if task == 'triggerBuild':
        from static import triggerBuild
        retval = triggerBuild.AsyncResult(task_id).get(timeout=1.0)
        return repr(retval)
    return jsonify({"Error": "Wrong taskID"})

# Server
@app.route("/task/server/<task>")
def serverWeb(task):
    if task == 'rebuildWikiPassword':
        from server import rebuildWikiPassword
        res = rebuildWikiPassword.apply_async([])
    elif task == 'monitorServices':
        from server import monitorServices
        res = monitorServices.apply_async([])
    elif task == 'monitorTechatNYUOrgWebsite':
        from server import monitorTechatNYUOrgWebsite
        res = monitorTechatNYUOrgWebsite.apply_async([])
    elif task == 'monitorCheckinWebsite':
        from server import monitorCheckinWebsite
        res = monitorCheckinWebsite.apply_async([])
    context = {"id": res.task_id}
    result = task + "()"
    goto = "{}".format(context['id'])
    return jsonify(result=result, goto=goto)

# Server Result
@app.route("/result/server/<task>/<task_id>")
def serverWebResult(task, task_id):
    if task == 'rebuildWikiPassword':
        from server import rebuildWikiPassword
        retval = rebuildWikiPassword.AsyncResult(task_id).get(timeout=1.0)
        return repr(retval)
    elif task == 'monitorServices':
        from server import monitorServices
        retval = monitorServices.AsyncResult(task_id).get(timeout=1.0)
        return repr(retval)
    elif task == 'monitorTechatNYUOrgWebsite':
        from server import monitorTechatNYUOrgWebsite
        retval = monitorTechatNYUOrgWebsite.AsyncResult(task_id).get(timeout=1.0)
        return repr(retval)
    elif task == 'monitorCheckinWebsite':
        from server import monitorCheckinWebsite
        retval = monitorCheckinWebsite.AsyncResult(task_id).get(timeout=1.0)
        return repr(retval)
    return jsonify({"Error": "Wrong taskID"})

# Backup
@app.route("/task/backup/<task>")
def backupWeb(task):
    if task == 'backupMySQLWithHost':
        from backup import backupMySQLWithHost
        res = backupMySQLWithHost.apply_async([])
        result = "backupMySQLWithHost()"
    elif task == 'backupMySQLWithoutHost':
        from backup import backupMySQLWithoutHost
        res = backupMySQLWithoutHost.apply_async([])
        result = "backupMySQLWithoutHost()"
    elif task == 'backupMongo':
        from backup import backupMongo
        res = backupMongo.apply_async([])
        result = "backupMongo()"
    context = {"id": res.task_id}
    goto = "{}".format(context['id'])
    return jsonify(result=result, goto=goto)

# Server Result
@app.route("/result/backup/<task>/<task_id>")
def backupWebResult(task, task_id):
    if task == 'backupMySQLWithHost':
        from backup import backupMySQLWithHost
        retval = backupMySQLWithHost.AsyncResult(task_id).get(timeout=1.0)
        return repr(retval)
    elif task == 'backupMySQLWithoutHost':
        from backup import backupMySQLWithoutHost
        retval = backupMySQLWithoutHost.AsyncResult(task_id).get(timeout=1.0)
        return repr(retval)
    elif task == 'backupMongo':
        from backup import backupMongo
        retval = backupMongo.AsyncResult(task_id).get(timeout=1.0)
        return repr(retval)
    return jsonify({"Error": "Wrong taskID"})

celery = make_celery(app)

if __name__ == "__main__":
    port = int(environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
