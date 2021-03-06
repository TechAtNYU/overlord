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
    'every-day-slack': {
        'task': 'static.trigger_build',
        'schedule': crontab(minute=0, hour=1),
        'args': ('slack-dump', 'master'),
    },
    'every-day-discuss': {
        'task': 'backup.backup_discuss',
        'schedule': crontab(minute=45, hour=2),
        'args': (),
    },
    'every-day-mailtrain': {
        'task': 'backup.backup_mailtrain_sql',
        'schedule': crontab(minute=30, hour=3),
        'args': (),
    },
    'every-thirty-minutes-event-attendance': {
        'task': 'orgsyncattendance.send_emails',
        'schedule': crontab(minute='*/30'),
        'args': ()
    },
    'every-day-feedback': {
        'task': 'feedback.send_emails',
        'schedule': crontab(minute=0, hour=23),
        'args': ()
    },
    'every-day-orgsync': {
        'task': 'orgsync.update_orgsync',
        'schedule': crontab(minute=0, hour=23),
        'args': ()
    },
    'every-day-reminder': {
        'task': 'reminder.send_emails',
        'schedule': crontab(minute=0, hour=07),
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
    'every-fourty-five-minutes-monitor-tnyu-site': {
        'task': 'server.monitor_techatnyu_org',
        'schedule': crontab(minute='*/45'),
        'args': (),
    },
}
