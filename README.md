Overlord now runs:

![Overlord](http://media.giphy.com/media/RFkWL5lqN3CZG/giphy-tumblr.gif)

- Reminder:
  - Sending reminder emails for unpublished events on the API
- Database backup on:
  - API server (MongoDB)
  - Business Development server (MySQL)
  - Jira (built-in)
  - Discuss (Postgres)
  - Slack conversations daily
- Monitoring and restarting:
  - techatnyu.org
  - services.tnyu.org
- Syncing
  - calendar-service
- Rebuilding static front-end for:
  - intranet
  - intranet-staging
  - startup-week
  - ship

Running overlord:

- `supervisord`
- `supervisorctl` (to see if everything starts)
- `nohup flower --port=5555 --basic_auth=tnyu:pw1 &` (run in background)
- To restart something: `supervisorctl restart celeryd` or `supervisorctl restart overlord`
- To stop something: `supervisorctl stop celeryd` (etc.)

Running tasks:

```python
from overlord import add

result = add.delay(1,1)
result.result
```

Long-running tasks vs one-off tasks

1. Long-running tasks don't need to be initiated by a person
2. One-off tasks can be initiated by a person through a HTTP request
