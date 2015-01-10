'''
types of events:
    NEW_GROUP -> when creating a new group
'''

from studybuddy.models import *
from studybuddy.utils import get_client_ip, ip_to_location
from datetime import date, datetime, time, timedelta
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
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
            import logging
            logging.exception(e)

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

def view_maps(request):
    ip_address = get_client_ip(request)
    lng, lat = ip_to_location(ip_address, default=True)

    vars_ = {'lng': lng,
             'lat': lat,
             'ip_address': ip_address}

    return render(request, "maps.jade", vars_)

@require_POST
@csrf_exempt
def create_study_session(request):
    from studybuddy.forms import NewStuddyGroupForm

    user = SM.getUser(request.session)
    if not user:
        print "no user"
        return HttpResponse(json.dumps({'status':'error','reason':'invalid user'}),content_type="application/json")

    form = NewStuddyGroupForm(request.POST)
    if form.is_valid():
        # continue adding
        print "form valid"
        try:
            var = form.cleaned_data
            loc = Location.create_or_get(var['here_id'],var['place_name'],(var['longitude'],var['latitude']))

            sg = StudyGroup(name=var['name'],
                            maxMembers=var['maxMembers'],
                            description=var['description'],
                            creator=user,
                            location=loc,
                            datetime=var['datetime'],
                            targetInterest=StudyInterest.getByName(var['targetInterest']),
                            targetChannels=InterestChannel.getByNames(var['targetChannels']))
            
            sg.save()

            study_interest = StudyInterest.getByName(var['targetInterest'])
            for c in InterestChannel.getByNames(var['targetChannels']):
                #send event!
                d = {
                    'type:' 'NEW_GROUP'
                    'interest_name': study_interest.name,
                    'channel_name': c.name
                }

                redis_server.publish("interest-%s.channel-%s"%(d['interest_name'], d['channel_name']), d)

            print "success"
            return HttpResponse(json.dumps({'status':'success'}),content_type="application/json")
        except Exception, e:
            import logging
            logging.exception(e)
    else:
        print request.POST
        print form.errors
        # return error

# Dashboard #####################################################################

def dashboardMain(request):
    return render(request, "dashboard.jade")

#Handlers for each event
def send_notifs(users):
    for u in users:
        #generate message_id using timestamp -- store in text    
        send_sms.delay(number=u.phone, message=msg)
        #other notif stuff
        print "users!"
        print u

def new_group(**args):
    #check for the keys in the data, kinda like RRSV
    if not 'interest_name' in data and not 'channel_name' in data:
        return

    interest_name = data['interest_name']
    channel_name= data['channel_name']

    interest = StudyInterest.objects.get(name=interest_name)
    channel = interest.channels.get(name=channel_name)
    users = channel.user_set.all()

    message = "" #create generate_message(event_name, user)

    send_notifs(users)

event_handler = {}
event_handler["NEW_GROUP"] = new_group
#add more for different events

#Callbacks for channel and group listeners
def channel_listener_callback(message):
    data = message['data']
    
    if not 'type' in data:
        return

    event_handler[data['type']](**data)

    print 'data!'
    print data
