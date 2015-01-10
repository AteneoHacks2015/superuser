from studybuddy.models import *

# Credentials must be a dictionary containing "username" and "password"
# and must both be valid.
def login(session, credentials):
    query = User.objects.filter(username=credentials["username"])

    if query.count() < 1:
        return False
    else:
        user = query.get()

    if user.checkPassword(credentials["password"]):
        session["user"] = user.id
        return True

    return False

def logout(session):
    session.flush()
    return True

# If user is logged in, returns user. Otherwise returns false.
def getUser(session):
    if "user" not in session:
        return False

    try:
        return User.objects.get(id=session["user"])
    except User.DoesNotExist:
        return False