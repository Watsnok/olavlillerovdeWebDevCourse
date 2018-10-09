from django.shortcuts import render
from django.http import HttpResponse
from .models import auction
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from yaasApplication.forms import UserCreationForm, changeEmailForm, auctionForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.utils import timezone
from django import forms
from datetime import date, datetime
from django.core.mail import send_mail
from django.conf import settings




# Create your views he

def home(request):
    auctions = auction.objects.all()
    return render(request, "auctions.html", {"auctions": auctions} )

def register(request):
        if request.method == 'POST':
            fm = UserCreationForm(request.POST)
            if fm.is_valid():
                fm.save()
                messages.success(request, 'Account created successfully')
        else:
            fm = UserCreationForm()

        return render(request, 'register.html', {'form': fm})

@login_required
def change_password(request):
    if(request.method=='POST'):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated')
            return redirect('index')
        else:
                messages.error(request, 'Please correct the error')

    else:
            form = PasswordChangeForm(request.user, request.POST)
    return render(request, 'change_password.html', {'form': form})

@login_required
def change_email(request):
    user = request.user
    if(request.method=='POST'):
        form = changeEmailForm(request.POST, request.user)
        if form.is_valid():
            user.email = form.cleaned_data['new_email']
            user.save()
            return redirect('index')
    else:
        form = changeEmailForm(request.POST, request.user)

    return render(request, 'change_email.html', {'form' : form})

@login_required
def create_auction(request):
    user = request.user
    newAuction = auction()
    if request.method == 'POST':
        form = auctionForm(request.POST, request.user)
        if form.is_valid():
            newAuction.title = form.cleaned_data['title']
            newAuction.seller = user
            newAuction.description = form.cleaned_data['description']
            newAuction.minprice = form.cleaned_data['minprice']
            newAuction.deadline = form.cleaned_data['deadline']
            if newAuction.checkDeadline(created=datetime.now(), deadline=form.cleaned_data['deadline']):
                newAuction.save()
                from_email = settings.EMAIL_HOST_USER
                to_email = [from_email, user.email]
                send_mail(subject="New Auction posted", message="Your auction was succesfully posted",
                          from_email=from_email, recipient_list=to_email, fail_silently=False,)
            return redirect('index')

    else:
        form = auctionForm(request.POST, request.user)

    return render(request, 'createAuction.html', {'form' : form})








