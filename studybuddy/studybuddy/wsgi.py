from gevent import Greenlet, monkey
monkey.patch_all(socket=True, dns=True, time=True, 
 select=True,thread=False, os=True, ssl=True, httplib=False, 
 aggressive=True) 

"""
WSGI config for studybuddy project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studybuddy.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

import redis

redis_server = redis.StrictRedis(host='localhost', port=6379, db=0)
pubsub = redis_server.pubsub()

from studybuddy.views import channel_listener_callback

def channels_listener(*args):
    print "kekekekek"
    pubsub.psubscribe(**{'interest-*\.channel-*':channel_listener_callback})
    while True:
        x = pubsub.get_message()
        
        '''
        if not isinstance(x, basestring):
            x'''


Greenlet.spawn(channels_listener)
