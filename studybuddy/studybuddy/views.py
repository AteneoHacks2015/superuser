from django.shortcuts import render, redirect
from django.http import HttpResponse
from studybuddy.models import *
import json

from studybuddy.celery import send_sms

import hashlib

def test(request):
    message_id = hashlib.md5('639474325719' + '6:42').hexdigest()
    send_sms.delay(number='639474325719', message='hi kix', message_id=message_id)
    return HttpResponse()

def createUser(request):
    if request.method == 'GET':
        return render(request, "user_create.jade")
    else:
        details = dict()
        for key, value in request.POST.items():
            if key != "interests":
                details[key] = value

        user = None
        try:
            user = User.createUser(details)
        except Exception, e:
            if e == "User already exists.": pass

        if user:
            for interest in request.POST.get("interests").split(","):
                user.addStudyInterest(interest)
            return redirect("/user/create/")

        return HttpResponse("Something went wrong!")

def studyInterestsQuery(request):
    results = StudyInterest.searchByName(request.GET.get("query"))
    result_list = []
    for result in results:
        result_list.append({"name": result.name, "id": result.id})

    return HttpResponse(json.dumps(result_list))
