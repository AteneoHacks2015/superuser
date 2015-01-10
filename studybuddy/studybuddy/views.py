from django.shortcuts import render, redirect
from django.http import HttpResponse

def createUser(request):
    return render(request, "page_template.jade")