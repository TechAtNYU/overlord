from celery.schedules import crontab

CELERY_TASK_SERIALIZER='json'
CELERY_ACCEPT_CONTENT=['json']
CELERY_RESULT_SERIALIZER='json'
CELERY_ENABLE_UTC=True
CELERY_TIMEZONE='America/New_York'
CELERYBEAT_SCHEDULE = {
  'every-day-api': {
      'task': 'backup.backupMongo',
      'schedule': crontab(minute=0, hour=0),
      'args': (),
  },
  'every-day-wiki': {
      'task': 'backup.backupMySQLWithHost',
      'schedule': crontab(minute=15, hour=0),
      'args': (),
  },
  'every-day-bd': {
      'task': 'backup.backupMySQLWithoutHost',
      'schedule': crontab(minute=30, hour=0),
      'args': (),
  },
  'every-day-wiki-password-change': {
      'task': 'server.rebuildWikiPassword',
      'schedule': crontab(minute=45, hour=0),
      'args': (),
  },
  'every-day-slack': {
      'task': 'static.triggerBuild',
      'schedule': crontab(minute=0, hour=1),
      'args': ('slack-dump', 'master'),
  },
    'every-day-jira': {
      'task': 'backup.backupJira',
      'schedule': crontab(minute=30, hour=2),
      'args': (),
  },
  'every-hour-intranet': {
      'task': 'static.triggerBuild',
      'schedule': crontab(minute='*/45'),
      'args': ('intranet', 'master'),
  },
  'every-hour-intranet-develop': {
      'task': 'static.triggerBuild',
      'schedule': crontab(minute='*/45'),
      'args': ('intranet', 'develop'),
  },
  'every-hour-startup-week': {
      'task': 'static.triggerBuild',
      'schedule': crontab(minute='*/45'),
      'args': ('startup-week', 'master'),
  },
  'every-hour-ship': {
      'task': 'static.triggerBuild',
      'schedule': crontab(minute='*/45'),
      'args': ('ship', 'master'),
  },
  'every-fifteen-minutes-calendar': {
      'task': 'static.triggerBuild',
      'schedule': crontab(minute='*/15'),
      'args': ('calendar-service', 'master'),
  },
  'every-fifteen-minutes-job-board': {
      'task': 'static.triggerBuild',
      'schedule': crontab(minute='*/15'),
      'args': ('job-board', 'master'),
  },
  'every-day-monitor-services': {
      'task': 'server.monitorServices',
      'schedule': crontab(minute='*/45'),
      'args': (),
  },
  'every-day-monitor-services': {
      'task': 'server.monitorTechatNYUOrgWebsite',
      'schedule': crontab(minute='*/45'),
      'args': (),
  },
  'every-day-monitor-services': {
      'task': 'server.monitorCheckinWebsite',
      'schedule': crontab(minute='*/45'),
      'args': (),
  },
}