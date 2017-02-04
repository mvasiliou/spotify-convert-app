from __future__ import absolute_import
from celery import Celery
from celery.schedules import crontab
import os

app = Celery('Music',
             include=['Music.tasks','spotify_convert.tasks'])

try:
    app.conf.update(BROKER_URL=os.environ['REDIS_URL'],
                    CELERY_RESULT_BACKEND=os.environ['REDIS_URL'])
except:
    app = Celery('MassContact',
                 broker = 'amqp://',
                 backend = 'amqp://',
                 include = ['Music.tasks', 'spotify_convert.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
        CELERY_TASK_RESULT_EXPIRES=3600,
        CELERYBEAT_SCHEDULE = {

        },
        CELERY_TIMEZONE = 'UTC'
    )

if __name__ == '__main__':
    app.start()