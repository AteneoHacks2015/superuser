from django.db import models
from django.core.exceptions import ObjectDoesNotExist

class InterestChannel(models.Model):
    name = models.CharField(max_length=32)

    @classmethod
    def getByNames(cls, names):
        try:
            return cls.objects.filter(name__in=names)
        except Exception, e:
            import logging
            logging.exception(e)
    @classmethod
    def searchByName(cls, keyword, interest):
        try:
            interest = StudyInterest.objects.get(id=interest)
        except StudyInterest.DoesNotExist:
            return []

        return interest.channels.filter(name__contains=keyword)

    @classmethod
    def create_or_get(cls, name):
        try:
            return cls.objects.get(name=name)
        except ObjectDoesNotExist:
            try:
                ic = InterestChannel(name=name)
                ic.save()
                print name," created as new InterestChannel"

                return ic
            except Exception, e:
                import logging
                logging.expcetion(e)

class StudyInterest(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField()
    channels = models.ManyToManyField(InterestChannel)

    @classmethod
    def searchByName(cls, keyword):
        return cls.objects.filter(name__contains=keyword)

    @classmethod
    def getByName(cls, name):
        try:
            return cls.objects.get(name=name)
        except Exception, e:
            import logging
            logging.exception(e)

class User(models.Model):
    username = models.CharField(max_length=32, unique=True)
    fullname = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    email = models.CharField(max_length=128)
    phone = models.CharField(max_length=32)
    university = models.CharField(max_length=128, blank=True, null=True)
    creationTime = models.DateTimeField(auto_now_add=True)
    interests = models.ManyToManyField(StudyInterest)
    channels = models.ManyToManyField(InterestChannel)

    # Instance Methods

    def setPassword(self, password):
        import hashlib
        self.password = hashlib.md5(password).hexdigest()
        self.save()

    def checkPassword(self, password):
        import hashlib
        if hashlib.md5(password).hexdigest() == self.password: return True
        return False

    def addStudyInterest(self, name):
        try:
            interest = StudyInterest.objects.get(name=name)
        except StudyInterest.DoesNotExist:
            interest = StudyInterest(name=name, description=name)
            interest.save()

        self.interests.add(interest)
        self.save()

    def removeStudyInterest(self, id):
        try:
            interest = StudyInterest.objects.get(id=id)
        except StudyInterest.DoesNotExist:
            return False

        self.interests.remove(interest)
        self.save()

    def addInterestChannel(self, name, interest):
        try:
            interest = StudyInterest.objects.get(id=interest)
        except StudyInterest.DoesNotExist:
            return False

        try:
            channel = interest.channels.get(name=name)
        except InterestChannel.DoesNotExist:
            channel = InterestChannel(name=name)
            channel.save()
            interest.channels.add(channel)
            interest.save()

        self.channels.add(channel)
        self.save()

    def removeInterestChannel(self, id):
        try:
            channel = self.channels.get(id=id)
        except InterestChannel.DoesNotExist:
            return False

        self.channels.remove(channel)
        self.save()


    # Class Methods

    @classmethod
    def createUser(cls, details):
        if cls.objects.filter(username=details['username']).count() > 0:
            raise Exception("User already exists.")

        # Create user record
        newUser = cls(
            username = details['username'],
            fullname = details['fullname'],
            email = details['email'],
            phone = details['phone'],
            university = details['university']
            )
        newUser.save()
        # Set user password
        newUser.setPassword(details['password'])

        return newUser

class Location(models.Model):
    name = models.CharField(max_length=32)
    here_id = models.CharField(max_length=64, unique=True)
    lng = models.DecimalField(max_digits=8,decimal_places=5)
    lat = models.DecimalField(max_digits=8,decimal_places=5)

    @classmethod
    def create_or_get(cls, here_id, name, long_lat):
        try:
            return Location.objects.get(here_id=here_id)

        except ObjectDoesNotExist:
            # create new instance of Location
            try:
                new_location = Location(name=name, here_id=here_id, lng=long_lat[0], lat=long_lat[1])
                new_location.save()

                return new_location
            except Exception, e:
                import logging
                logging.exception(e)

class StudyGroup(models.Model):
    name = models.CharField(max_length=32)
    maxMembers = models.IntegerField()  # set to 0 for unlimited
    description = models.TextField()
    creator = models.ForeignKey(User, related_name='creator')
    location = models.ForeignKey(Location)
    datetime = models.DateTimeField()
    targetInterest = models.ForeignKey(StudyInterest)
    targetChannels = models.ManyToManyField(InterestChannel)
    members = models.ManyToManyField(User, related_name='members')
    creationTime = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    text = models.TextField()
    sourceUser = models.ForeignKey(User, null=True, blank=True, related_name='sourceUser')
    targetUser = models.ForeignKey(User, related_name='targetUser')
    status = models.CharField(max_length=2, choices=(('0', 'Unread'), ('1', 'Read')))
    creationTime = models.DateTimeField(auto_now_add=True)
    studyGroup = models.ForeignKey(StudyGroup)
