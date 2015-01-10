from studybuddy.models import *
from studybuddy.utils import get_client_ip, ip_to_location
from datetime import date, datetime, time, timedelta
from django.shortcuts import render, redirect
from django.http import HttpResponse
from studybuddy.models import *
from studybuddy import sessionmanager as SM
import json
from studybuddy.celery import send_sms, debug_task
import hashlib

import redis

redis_server = redis.StrictRedis(host='localhost', port=6379, db=0)
pubsub = redis_server.pubsub()

def test(request):
    message_id = hashlib.md5('639474325719' + '6:42').hexdigest()
    #send_sms.delay(number='639474325719', message='hi kix', message_id=message_id)
    
    x = {
        'interest_name':'lol',
        'channel_name':'lol'
    }

    redis_server.publish("interest-%s.channel-%s"%(x['interest_name'], x['channel_name']), x)
    
    return HttpResponse()

# User Account Views #####################################################################
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

# AJAX Query Endpoints #####################################################################

def studyInterestsQuery(request):
    results = StudyInterest.searchByName(request.GET.get("query"))
    result_list = []
    for result in results:
        result_list.append({"name": result.name, "id": result.id})

    return HttpResponse(json.dumps(result_list))

def userStudyInterestsQuery(request):
    user = SM.getUser(request.session)
    if not user:
        return HttpResponse("[]")

    else:
        userSIList = []
        for SI in user.interests.all():
            userSIList.append({"id": SI.id, "name":SI.name})
        return HttpResponse(json.dumps(userSIList))

def userStudyInterestsUpdate(request):
    print json.dumps(request.POST)
    try:
        user = SM.getUser(request.session)
        if not user:
            return HttpResponse("Bad request.")

        else:
            if "removal" in request.POST and request.POST.get("removal") != "":
                for remove in request.POST.get("removal").split(","):
                    user.removeStudyInterest(remove)
            if "addition" in request.POST and request.POST.get("addition") != "":
                for add in request.POST.get("addition").split(","):
                    user.addStudyInterest(add)
    except Exception, e:
        return HttpResponse("Error. %s"%e)
    return HttpResponse("OK")

def create_study_session(request):
    ip_address = get_client_ip(request)
    lng, lat = ip_to_location(ip_address, default=True)

    vars_ = {'lng': lng,
             'lat': lat,
             'ip_address': ip_address}

    return render(request, "maps.jade", vars_)

# Dashboard #####################################################################

def dashboardMain(request):
    return render(request, "dashboard.jade")


#Callbacks for channel and group listeners
def channel_listener_callback(message):
    data = message['data']
    
    #check for the keys in the data, kinda like RRSV
    if not 'interest_name' in data and not 'channel_name' in data:
        return

    #interest_name = data['interest_name']
    #channel_name= data['channel_name']

    #interest = StudyInterest.objects.get(name=interest_name)
    #channel = interest.channels.get(name=channel_name)
    #users = channel.user_set.all()

    #generate message_id using timestamp

    #send message based on change

    '''
    for u in users:
        #send_sms.delay(number=u.phone, message=msg, message_id="")
        print "users!"
        print u'''

    print 'data!'
    print data
