from __future__ import absolute_import

import os

from celery import Celery

from studybuddy.lib import chikka

from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studybuddy.settings')

app = Celery('proj')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print('topkek {0!r}'.format(self.request))

@app.task(bind=True)
def send_sms(self, number="", message="", message_id=""):
    print('topkek {0!r}'.format(self.request))
    r = chikka.send_sms(number, message, message_id)
    print('kek {0!r}'.format(r.json()))
