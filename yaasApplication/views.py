from django.shortcuts import render
from django.http import HttpResponse
from .models import auction
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from yaasApplication.forms import UserCreationForm, changeEmailForm, auctionForm, editDescriptionForm, bidForm
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
from django.db.models import Q





# Create your views he

def home(request):
    auctions = auction.objects.all()
    auctions = auctions.filter(isBanned=False)
    return render(request, "auctions.html", {"auctions": auctions})

@login_required
def banAuction(request, id):
    currauction = auction.objects.get(pk=id)
    user = request.user
    if user.is_superuser:
        if request.method == 'GET':
            currauction.banAuction()
            currauction.save()
    else:
        messages.error(request, "You have to be superuser in order to ban an auction")

    return render(request, 'ban_auction.html')

@login_required
def banned_auctions(request):
    user = request.user
    if user.is_superuser:
        banned_auctions = auction.objects.all()
        banned_auctions = banned_auctions.filter(isBanned=True)
        return render(request, 'banned_auctions.html', {'auctions': banned_auctions})
    else:
        messages.error(request, "You have to be superuser in order to view banned auctions")

    return redirect('index')

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
            messages.success(request, "Email was successfully changed")
            return redirect('index')
    else:
        form = changeEmailForm(request.POST, request.user)

    return render(request, 'change_email.html', {'form' : form})

@login_required
def edit_auction(request, id):
    currauction = auction.objects.get(pk=id)
    if request.method == 'POST':
        form = editDescriptionForm(request.POST, request.user)
        if form.is_valid():

            currauction.description = form.cleaned_data['description']
            currauction.save()
            messages.succes(request, "Edit successful")
            return redirect('index')
        else:
            messages.error(request, "Description was not accepted. Please try again")

    else:
        form = editDescriptionForm(request.POST, request.user)

    return render(request, 'edit_auction.html', {'form' : form})

@login_required
def place_bid(request, id):
    # Add mutex? Semaphor
    currauction = auction.objects.get(pk=id)
    user = request.user
    if user == currauction.getWinner():
        messages.error(request, "You are already winning this auction.")
    if request.method == 'POST':
        form = bidForm(request.POST, request.user)
        if form.is_valid():
            temp = form.cleaned_data['bid']
            temp = round(temp, 2)
            increase = (float(temp) - float(currauction.currentBid))
            # Check if Bid is higher than current bid, minprice and above minimum increment
            if currauction.currentBid <= temp and currauction.minprice < temp and increase >= 0.01:
                currauction.currentBid = temp
                currauction.setWinner(user)
                currauction.addBidder(user)
                print(currauction.getBidders())
                currauction.save()
                currauction.notifySeller("newbid")
                currauction.notifyWinner("newbid")
            else:
                messages.error(request, "Bid was not accepted. Bid needs to higher than minprice and current bid "
                                        "and must be higher than 0,01")
    else:
        form = bidForm(request.POST, request.user)

    return render(request, 'place_bid.html', {'form': form, 'auction': currauction})



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
                messages.success(request, "Auction was created")
                return redirect('index')
            else:
                messages.error(request, "Auctions duration must be 27 hours")
            return redirect('index')

    else:
        form = auctionForm(request.POST, request.user)

    return render(request, 'createAuction.html', {'form' : form})

@login_required
def my_auctions(request):
    user = request.user
    all_auctions = auction.objects.all()
    auctions = []
    for item in all_auctions:
        if user == item.seller and item.isBanned is False:
            auctions.append(item)
    return render(request, 'my_auctions.html', {'auctions': auctions})


def search_auction(request):
    result = request.GET.get("search_auction")
    auctions = auction.objects.all()
    if result:
        auctions = auctions.filter(Q(title__icontains=result))
        auctions = auctions.filter(is_active=True)
        auctions = auctions.filter(isBanned=False)

    return render(request, 'search_results.html', {'auctions': auctions})