from __future__ import absolute_import

import os

from celery import Celery

from studybuddy.lib import chikka

from django.conf import settings

import hashlib

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studybuddy.settings')

app = Celery('proj')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self, t):
    print('topkek {0!r}'.format(t))

@app.task(bind=True)
def send_sms(self, number="", message=""):
    print('topkek {0!r}'.format(self.request))

    date_str = datetime.strftime(datetime.now, "%d/%m/%y %H:%M")

    md5 = hashlib.md5()
    md5.update(number + date_str)
    h = md5.hexdigest()

    r = chikka.send_sms(number, message, h)
    print('kek {0!r}'.format(r.json()))

@app.task(bind=True)
def send_notification(self, number="", message="", message_id=""):
    chikka.send_sms(number, message, message_id) 
