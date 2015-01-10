from django.db import models

class User(models.Model):
    username = models.CharField(max_length=32, unique=True)
    fullname = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    email = models.CharField(max_length=128)
    phone = models.CharField(max_length=32)
    university = models.CharField(max_length=128, blank=True, null=True)
    creationTime = models.DateTimeField(auto_now_add=True)

    # Instance Methods

    def setPassword(self, password):
        import hashlib
        self.password = hashlib.md5(password).hexdigest()
        self.save()

    def checkPassword(self, password):
        import hashlib
        if hashlib.md5(password).hexdigest() == self.password: return True
        return False

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


class InterestChannel(models.Model):
    name = models.CharField(max_length=32)

class StudyInterest(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField()
    channels = models.ManyToManyField(InterestChannel)

class StudyGroup(models.Model):
    maxMembers = models.IntegerField()
    description = models.TextField()
    creator = models.ForeignKey(User, related_name='creator')
    location = models.TextField()
    datetime = models.DateTimeField()
    targetInterest = models.ForeignKey(StudyInterest)
    targetChannels = models.ManyToManyField(InterestChannel, null=True, blank=True)
    members = models.ManyToManyField(User, related_name='members')
    isPrivate = models.BooleanField(default=False)
    creationTime = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    text = models.TextField()
    sourceUser = models.ForeignKey(User, null=True, blank=True, related_name='sourceUser')
    targetUser = models.ForeignKey(User, related_name='targetUser')
    status = models.CharField(max_length=2, choices=(('0', 'Unread'), ('1', 'Read')))
    creationTime = models.DateTimeField(auto_now_add=True)
    studyGroup = models.ForeignKey(StudyGroup)