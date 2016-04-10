from celery.schedules import crontab

CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = 'America/New_York'
CELERYBEAT_SCHEDULE = {
    'every-day-api': {
        'task': 'backup.backup_mongo',
        'schedule': crontab(minute=0, hour=0),
        'args': (),
    },
    'every-day-bd': {
        'task': 'backup.backup_bd_mysql',
        'schedule': crontab(minute=30, hour=0),
        'args': (),
    },
    'every-day-slack': {
        'task': 'static.trigger_build',
        'schedule': crontab(minute=0, hour=1),
        'args': ('slack-dump', 'master'),
    },
    'every-day-jira': {
        'task': 'backup.backup_jira',
        'schedule': crontab(minute=30, hour=2),
        'args': (),
    },
    'every-day-discuss': {
        'task': 'backup.backup_discuss',
        'schedule': crontab(minute=45, hour=2),
        'args': (),
    },
    'every-day-feedback': {
        'task': 'feedback.send_emails',
        'schedule': crontab(minute=0, hour=9),
        'args': ()
    },
    'every-fourty-five-minutes-intranet': {
        'task': 'static.trigger_build',
        'schedule': crontab(minute='*/45'),
        'args': ('intranet', 'master'),
    },
    'every-fourty-five-minutes-intranet-develop': {
        'task': 'static.trigger_build',
        'schedule': crontab(minute='*/45'),
        'args': ('intranet', 'develop'),
    },
    'every-fourty-five-minutes-startup-week': {
        'task': 'static.trigger_build',
        'schedule': crontab(minute='*/45'),
        'args': ('startup-week', 'v2'),
    },
    'every-fourty-five-minutes-ship': {
        'task': 'static.trigger_build',
        'schedule': crontab(minute='*/45'),
        'args': ('ship', 'master'),
    },
    'every-fifteen-minutes-calendar': {
        'task': 'static.trigger_build',
        'schedule': crontab(minute='*/15'),
        'args': ('calendar-service', 'master'),
    },
    'every-fourty-five-minutes-job-board': {
        'task': 'static.trigger_build',
        'schedule': crontab(minute='*/15'),
        'args': ('job-board', 'v3'),
    },
    'every-fourty-five-minutes-monitor-services': {
        'task': 'server.monitor_services',
        'schedule': crontab(minute='*/45'),
        'args': (),
    },
    'every-fourty-five-minutes-monitor-tnyu-site': {
        'task': 'server.monitor_techatnyu_org',
        'schedule': crontab(minute='*/45'),
        'args': (),
    },
}
