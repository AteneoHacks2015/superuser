from django.shortcuts import render, redirect
from django.http import HttpResponse

from studybuddy.celery import send_sms

import hashlib

def test(request):
    message_id = hashlib.md5('639474325719' + '6:42').hexdigest()
    send_sms.delay(number='639474325719', message='hi kix', message_id=message_id)
    return HttpResponse()

def createUser(request):
    return render(request, "user_create.jade")
