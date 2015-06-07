from celery.schedules import crontab

CELERY_TASK_SERIALIZER='json'
CELERY_ACCEPT_CONTENT=['json']
CELERY_RESULT_SERIALIZER='json'
CELERY_ENABLE_UTC=True
CELERY_TIMEZONE='America/New_York'
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
  'every-day-bd': {
      'task': 'overlord.backupMySQLWithoutHost',
      'schedule': crontab(minute=0, hour=2),
      'args': (),
  },
  'every-hour-intranet': {
      'task': 'overlord.triggerBuild',
      'schedule': crontab(minute='*/45'),
      'args': ('intranet', 'master'),
  },
  'every-hour-intranet-develop': {
      'task': 'overlord.triggerBuild',
      'schedule': crontab(minute='*/45'),
      'args': ('intranet', 'develop'),
  },
  'every-hour-startup-week': {
      'task': 'overlord.triggerBuild',
      'schedule': crontab(minute='*/45'),
      'args': ('startup-week', 'master'),
  },
  'every-hour-ship': {
      'task': 'overlord.triggerBuild',
      'schedule': crontab(minute='*/45'),
      'args': ('ship', 'master'),
  },
  'every-fifteen-minutes-calendar': {
      'task': 'overlord.triggerBuild',
      'schedule': crontab(minute='*/15'),
      'args': ('calendar-service', 'master'),
  },
}