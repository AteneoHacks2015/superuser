from studybuddy.models import *
from studybuddy.utils import get_client_ip, ip_to_location
from datetime import date, datetime, time, timedelta
from django.shortcuts import render, redirect
from django.http import HttpResponse
from studybuddy.models import *
from studybuddy import sessionmanager as SM
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

def loginUser(request):
    if request.method == 'GET':
        return render(request, "user_login.jade")
    else:
        SM.login(request.session, request.POST)
        return redirect("/")
def logoutUser(request):
    SM.logout(request.session)
    return redirect("/")

def studyInterestsQuery(request):
    results = StudyInterest.searchByName(request.GET.get("query"))
    result_list = []
    for result in results:
        result_list.append({"name": result.name, "id": result.id})

    return HttpResponse(json.dumps(result_list))

def create_study_session(request):
    ip_address = get_client_ip(request)
    lng, lat = ip_to_location(ip_address, default=True)

    vars_ = {'lng': lng, 
             'lat': lat,
             'ip_address': ip_address}

    return render(request, "maps.jade", vars_)
