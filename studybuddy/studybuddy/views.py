import hashlib

from django.http import HttpResponse
from studybuddy.celery import send_sms

def test(request):
    message_id = hashlib.md5('639474325719' + '6:42').hexdigest()
    send_sms.delay(number='639474325719', message='hi kix', message_id=message_id)
    return HttpResponse()
