'''
types of events:
    NEW_GROUP -> when creating a new group
'''

from studybuddy.models import *
from django.core.exceptions import ObjectDoesNotExist
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
from datetime import datetime

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
            return redirect("/dashboard/")

        return HttpResponse("Something went wrong!")

def loginUser(request):
    if SM.getUser(request.session):
        return redirect('/dashboard/')
    if request.method == 'GET':
        return render(request, "user_login.jade")
    else:
        SM.login(request.session, request.POST)
        return redirect("/dashboard/")
def logoutUser(request):
    SM.logout(request.session)
    return redirect("/user/login/")

# AJAX Query Endpoints #####################################################################

def studyInterestsQuery(request):
    results = StudyInterest.searchByName(request.GET.get("term"))

    result_list = []
    for result in results:
        result_list.append({"text": result.name, "id": result.id})

    return HttpResponse(json.dumps({"results": result_list}))

def interestChannelsQuery(request):
    results = InterestChannel.searchByName(request.GET.get("term"), request.GET.get("interest"))
    result_list = []
    for result in results:
        result_list.append({"text": result.name, "id": result.id})

    return HttpResponse(json.dumps({"results": result_list}))

def userInterestChannelsQuery(request):
    user = SM.getUser(request.session)
    if not user:
        return HttpResponse("[]")

    else:
        userCHList = []
        try:
            for CH in user.channels.all():
                if CH in StudyInterest.objects.get(id=request.GET.get("interest")).channels.all():
                    userCHList.append({"id": CH.id, "name": CH.name})
            return HttpResponse(json.dumps(userCHList))
        except Exception, e:
            return HttpResponse("Error. %s"%e)

def userInterestChannelsUpdate(request):
    print json.dumps(request.POST)
    try:
        user = SM.getUser(request.session)
        if not user:
            return HttpResponse("Bad request.")

        if "addition" in request.POST and request.POST.get("addition") != "":
            for add in request.POST.get("addition").split(","):
                user.addInterestChannel(add, request.POST.get("interest"))
        if "removal" in request.POST and request.POST.get("removal") != "":
            for remove in request.POST.get("removal"):
                user.removeInterestChannel(remove)
        return HttpResponse("OK")
    except Exception, e:
        return HttpResponse("Error. %s"%e)

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

def get_study_sessions(request):
    if not SM.getUser(request.session):
        return redirect('/user/login/')
    from datetime import datetime
    from django.utils import timezone
    try:
        here_id = request.GET.get('here_id')
        place = Location.objects.get(here_id=here_id)
        sgs = StudyGroup.objects.filter(location=place).exclude(datetime__lt=timezone.now())
        resp = []

        for sg in sgs:
            resp.append({'name':sg.name, 'datetime': datetime.strftime(sg.datetime,'%y/%m/%d %H:%M'), 'interest': sg.targetInterest.name, 'host': sg.creator.username})

        print resp
        return HttpResponse(json.dumps(resp),content_type="application/json")

    except ObjectDoesNotExist:
        pass
    except Exception, e:
        import logging
        logging.exception(e)

    return HttpResponse(json.dumps([]),content_type="application/json")

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
            print var
            loc = Location.create_or_get(var['here_id'],var['place_name'],(var['longitude'],var['latitude']))

            sg = StudyGroup(name=var['name'],
                            maxMembers=var['maxMembers'],
                            description=var['description'],
                            creator=user,
                            location=loc,
                            datetime=var['datetime'],
                            targetInterest=StudyInterest.objects.get(id=var['targetInterest']))

            sg.save()

            '''send_sms.delay()

            study_interest = StudyInterest.objects.get(id=var['targetInterest'])
            for c in InterestChannel.getByNames(var['targetChannels']):
                print "weh"
                #send event!
                d = {
                    'type': 'NEW_GROUP',
                    'group_name': var['name'],
                    'interest_name': study_interest.name,
                    'channel_name': c.name,
                    'datetime': datetime.strftime(sg.datetime, '%y/%m/%d %H:%M')
                }

                redis_server.publish("interest-%s.channel-%s"%(d['interest_name'], d['channel_name']), d)'''
            study_interest = StudyInterest.objects.get(id=var['targetInterest'])
            for c in InterestChannel.getByNames(var['targetChannels']):
                d = {
                    'type': 'NEW_GROUP',
                    'group_name': var['name'],
                    'interest_name': study_interest.name,
                    'channel_name': c.name,
                    'datetime': datetime.strftime(sg.datetime, '%y/%m/%d %H:%M')
                }
                new_group(**d)

            for channel in var['targetChannels'].split(' '):
                tc = InterestChannel.create_or_get(channel)
                sg.targetChannels.add(tc)

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
    user = SM.getUser(request.session)
    if not user:
        return redirect('/user/login/')


    ms = StudyGroup.objects.filter(creator=user)

    return render(request, "dashboard.jade", {'my_sessions':ms})

#Handlers for each event
def send_notifs(users, msg):
    for u in users:
        #generate message_id using timestamp
        send_sms.delay(number=u.phone, message=msg)
        #other notif stuff
        print "users!"
        print u

def generate_message(event_name, **args):
    message = ""
    if event_name == 'NEW_GROUP':
        if not 'group_name' in args and not 'interest_name' in args:
            print '\n\n\n\nno group and interest_name'
            return
        if not 'datetime' in args:
            print '\n\n\n\nno datetime\n\n\n\n'
            return

        message = "New relevant study grp. as of %s:\n\n"% (args['datetime'])


        message += "%s\n"%(args['group_name'])
        message += "%s"%(args['interest_name'])

        for c in args['channel_name']:
            message += "#%s"%(c)

    return message

def new_group(**args):
    #check for the keys in the data, kinda like RRSV
    if not 'interest_name' in args and not 'channel_name' in args:
        print "\n\n\n\nuh oh\n\n\n\n"
        return

    interest_name = args['interest_name']
    channel_name= args['channel_name']

    interest = StudyInterest.objects.get(name=interest_name)
    channel = interest.channels.get(name=channel_name)
    users = channel.user_set.all()

    print 'users'
    print users


    message = generate_message('NEW_GROUP', **args) #create generate_message(event_name, **args)

    if len(message) > 0:
        send_notifs(users, message)

event_handler = {}
event_handler["NEW_GROUP"] = new_group
#add more for different events

#Callbacks for channel and group listeners
def channel_listener_callback(message):
    msg = json.loads(message['data'].replace(" u'"," '"))
    print "\n\n\n\n\n\n\n\n"
    print msg['data']

    print type(msg['data'])
    data = msg

    print "\n\n\n\n\n\n\n\n"


    print type(data)
    new_group(**data)

    print 'data!'
    print data
