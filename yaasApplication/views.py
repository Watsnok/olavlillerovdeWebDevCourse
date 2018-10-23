from django.shortcuts import render
from django.http import HttpResponse
from .models import auction, userInfo
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from yaasApplication.forms import UserCreationForm, changeEmailForm, auctionForm, editDescriptionForm, bidForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect, render_to_response
from django.utils import timezone
from django import forms
from datetime import date, datetime
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from django.template import RequestContext
from django.views import i18n
from django.urls import reverse
from django.utils import translation
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect





# Create your views he

def home(request):
    auctions = auction.objects.all()
    auctions = auctions.filter(isBanned=False)
    auctions = auctions.filter(is_active=True)
    return render(request, "auctions.html", {"auctions": auctions})

def loginuser(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            if userInfo.exists(user):
                lang = userInfo.getLang(user)
                request.session[translation.LANGUAGE_SESSION_KEY] = lang

            messages.success(request, "Login successful")
            user.save()

        else:
            messages.error(request, "Wrong username or password")
            return redirect('login')
            #return HttpResponseRedirect(request.GET.get("next", reverse("login")))



    else:
        return render(request, "login.html", {"next": request.GET.get("next", reverse("index"))})

    return redirect('index')


def lougoutuser(request):
    logout(request)
    return redirect('index')

@login_required
def banAuction(request, id):
    currauction = auction.objects.get(pk=id)
    user = request.user

    if user.is_superuser:
        if request.method == 'GET':
            currauction.banAuction()
            currauction.is_active = False
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
            us = userInfo()
            us.username = fm.cleaned_data['username']
            us.language = fm.cleaned_data['language']
            us.email = fm.cleaned_data['email']
            us.save()
            fm.save()
            messages.success(request, 'Account created successfully')
            return redirect('index')
    else:
        fm = UserCreationForm()

    return render(request, 'register.html', {'form': fm})


@login_required
def change_password(request):
    if request.method == 'POST':
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
    if request.method == 'POST':
        form = changeEmailForm(request.POST, request.user)
        if form.is_valid():
            user.email = form.cleaned_data['new_email']
            user.save()
            messages.success(request, "Email was successfully changed")
            return redirect('index')
    else:
        form = changeEmailForm(request.POST, request.user)

    return render(request, 'change_email.html', {'form': form})


@login_required
def edit_auction(request, id):
    print("lang" in request.COOKIES)
    currauction = auction.objects.get(pk=id)
    if currauction.lockedby == "":
        currauction.lockedby = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
        messages.success(request, "The page is locked")
        currauction.save()
    elif currauction.lockedby != request.COOKIES.get(settings.SESSION_COOKIE_NAME):
        return render("locked.html", {'auction': currauction})

    if request.method == 'POST':

        form = editDescriptionForm(request.POST, request.user)
        if form.is_valid():
            currauction.description = form.cleaned_data['description']
            messages.success(request, "Edit successful")
            currauction.lockedby = ""
            messages.success(request, "The lock is lifted")
            currauction.save()
            return redirect('index')
        else:
            messages.error(request, "Description was not accepted. Please try again")

    else:
        form = editDescriptionForm(request.POST, request.user)

    return render(request, 'edit_auction.html', {'form': form})


@login_required
def place_bid(request, id):
    currauction = auction.objects.get(pk=id)
    user = request.user

    if user == currauction.getWinner():
        messages.error(request, "You are already winning this auction.")

    elif currauction.lockedby == "":
        currauction.lockedby = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
        messages.success(request, "The page is locked")
        currauction.save()
    elif currauction.lockedby != request.COOKIES.get(settings.SESSION_COOKIE_NAME):
        #return render_to_response(request, "locked.html", {'auction': currauction})
        return redirect('index')

    if request.method == 'POST':
        form = bidForm(request.POST, request.user)
        if form.is_valid():
            temp = form.cleaned_data['bid']
            temp = round(temp, 2)
            increase = (float(temp) - float(currauction.currentBid))
            # Check if Bid is higher than current bid, minprice and above minimum increment
            if currauction.currentBid <= temp and currauction.minprice < temp and increase >= 0.01\
                    and not currauction.isBanned and currauction.is_active:
                currauction.currentBid = temp
                currauction.setWinner(user)
                currauction.addBidder(user)

                #if diff < datetime.now:
                diff = currauction.deadline - timezone.timedelta(minutes=5)
                now = datetime.now()
                if currauction.checkDeadline(created=currauction.created_at, deadline=currauction.deadline,
                                             reason="minutes"):
                    currauction.deadline = currauction.deadline + timezone.timedelta(minutes=5)

                currauction.lockedby = ""
                messages.success(request, "The lock is lifted")
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
            if newAuction.minprice < 0:
                messages.error(request, "Minimum price can not be a negative number")

            elif newAuction.checkDeadline(created=datetime.now(), deadline=form.cleaned_data['deadline'], reason="days"):
                newAuction.save()
                from_email = settings.EMAIL_HOST_USER
                print(user.email)
                to_email = [from_email, user.email]
                send_mail(subject="New Auction posted", message="Your auction was succesfully posted",
                          from_email=from_email, recipient_list=to_email, fail_silently=False, )
                messages.success(request, "Auction was created")
                return redirect('index')
            else:
                messages.error(request, "Auctions duration must be 27 hours")
            return redirect('create_auction')

    else:
        form = auctionForm(request.POST, request.user)

    return render(request, 'createAuction.html', {'form': form})


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
