from django.db import models

class User(models.Model):
    username = models.CharField(max_length=32)
    fullname = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    email = models.CharField(max_length=128)
    phone = models.CharField(max_length=32)
    university = models.CharField(max_length=128, blank=True, null=True)

    def setPassword(self, password):
        import hashlib
        self.password = hashlib.md5(password).digest()
        self.save()

    def checkPassword(self, password):
        import hashlib
        if hashlib.md5(password).digest() == self.password: return True
        return False


class InterestChannel(models.Model):
    name = models.CharField(max_length=32)

class StudyInterest(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField()
    channels = models.ManyToManyField(InterestChannel)

class StudyGroup(models.Model):
    maxMembers = models.IntegerField()
    description = models.TextField()
    creator = models.ForeignKey(User)
    location = models.TextField()
    time = models.DateTimeField()
    targetInterest = models.ForeignKey(StudyInterest)
    targetChannels = models.ManyToManyField(InterestChannel, null=True, blank=True)
    members = models.ManyToManyField(User)
    isPrivate = models.BooleanField(default=False)
    creationTime = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    text = models.TextField()
    sourceUser = models.ForeignKey(User, null=True, blank=True)
    targetUser = models.ForeignKey(User)
    status = models.CharField(max_length=2, choices=(('0', 'Unread'), ('1', 'Read')))
    creationTime = models.DateTimeField(auto_now_add=True)
    studyGroup = models.ForeignKey(StudyGroup)