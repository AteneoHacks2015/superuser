def SMVars(request):
    from studybuddy import sessionmanager as SM
    return {'SMUser': SM.getUser(request.session)}