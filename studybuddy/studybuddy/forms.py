from django import forms

class NewStuddyGroupForm(forms.Form):
	name = forms.CharField() #StudyGroup name
	maxMembers = forms.IntegerField()
	description = forms.CharField(max_length=255,required=False)
	datetime = forms.DateTimeField(input_formats=['%Y/%m/%d %H:%M'])
	targetInterest = forms.CharField(max_length=255)
	targetChannels = forms.CharField(max_length=255) #array of channel ids
	# members = forms.MultipleChoiceField(required=False)

	#auxilary information not needed by StudyGroup model
	#but needed in case new Location is to be created
	place_name = forms.CharField(max_length=32)
	here_id = forms.CharField(max_length=64)
	longitude = forms.DecimalField(decimal_places=5,max_digits=8)
	latitude = forms.DecimalField(decimal_places=5,max_digits=8)