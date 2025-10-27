from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Section

# Create your views here.
def homepage(request):
    return render(request, 'groupme_app/homepage.html')
