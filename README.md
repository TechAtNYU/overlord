# Overlord

Overlord now runs:

![Overlord](http://media.giphy.com/media/RFkWL5lqN3CZG/giphy-tumblr.gif)

#### Features
- Database backup on (backup.py):
  - API server (MongoDB)
  - Jira (built-in)
  - Discuss (Postgres)
  - Slack conversations daily
- Monitoring and restarting (server.py):
  - techatnyu.org
  - services.tnyu.org
- Rebuilding static front-end for (static.py):
  - intranet
  - intranet-staging
  - startup-week
  - ship

#### Running Overlord (in development):

- Install dependencies with `$ pip install -r requirements.txt`
- Install and/or run [RabbitMQ](https://www.rabbitmq.com/).
- `$ celery -A overlord.celery worker --loglevel=info &` (run in background)

#### Running Overlord (in production):

- Install dependencies with `$ pip install -r requirements.txt`
- `$ supervisord`
- `$ supervisorctl` (to see if everything starts)
- `$ nohup flower --port=5555 --basic_auth=tnyu:pw1 &` (run in background)
- To restart something: `$ supervisorctl restart celeryd` or `supervisorctl restart overlord`
- To stop something: `$ supervisorctl stop celeryd` (etc.)
