from django.shortcuts import render
from django.http import HttpResponse
from .models import auction, user


# Create your views he

def home(request):
    auctions = auction.objects.all()
    user.objects.all()
    return render(request, "auctions.html", {"auctions": auctions} )
