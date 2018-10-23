from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
from django import forms
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import auth
import django.contrib.auth.base_user as auth_base
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User



# Create your models here.

class userInfo(models.Model):
    username = models.CharField(max_length=40)
    language = models.CharField(max_length=10)
    email = models.CharField(max_length=50, default="")

    @classmethod
    def exists(cls, user):
        return len(cls.objects.filter(username=user)) > 0

    @classmethod
    def getLang(cls, user):
        return cls.objects.get(username=user).language

    @classmethod
    def getEmail(cls, user):
        if user.is_superuser:
            return "olav.lillerovde@gmail.com"
        else:
            return cls.objects.get(username=user).email



class auction(models.Model):
    title = models.CharField(max_length=30)
    seller = models.ForeignKey(User, related_name="auctions", on_delete=models.CASCADE)
    description = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    minprice = models.IntegerField()
    deadline = models.DateTimeField()
    is_active = models.BooleanField(auto_created=True, default=True)
    currentBid = models.DecimalField(default=0, auto_created=True, decimal_places=2, max_digits=6)
    winner = models.ForeignKey(User, default=None, on_delete=models.CASCADE, null=True)
    isBanned = models.BooleanField(auto_created=True, default=False)
    bidders = []
    lockedby = models.TextField(default="")
    timelock = 0

    def __str__(self):
        return self.title

    def getTimeLock(self):
        temp = self.timelock
        return temp

    def incrementTimeLock(self):
        self.timelock += 1

    def addBidder(self, bidder):
        if bidder not in self.bidders:
            self.bidders.append(bidder)

    def getBidders(self):
        return self.bidders

    def checkDeadline(self, created, deadline, reason):
        if reason == "days":
            duration = datetime.timedelta(days=3)
            diff = deadline - duration
            if (diff.year < created.year) or (diff.year == created.year and diff.month == created.month
                                          and diff.day <= created.day) or (diff.year == created.year
                                                                           and diff.month < created.month):
            # raise forms.ValidationError("Duration must be longer than 72 hours")
                return False
            else:
                return True

        elif reason == "minutes":
            duration = datetime.timedelta(minutes=5)
            diff = deadline - duration
            now = datetime.datetime.now()
            if (diff.year < now.year) or (diff.year == now.year and diff.month == now.month
                                              and diff.day <= now.day) or (diff.year == now.year
                                                                               and diff.month < now.month):
                # raise forms.ValidationError("Duration must be longer than 72 hours")
                return True
            else:
                return False

    def banAuction(self):
        # Notify all bidders
        # Notify seller
        # Cant bid on banned auction
        # Admin only can ban auctions
        # Admin only can view banned auctions
        # Banned auctions are not resolved

        self.isBanned = True
        self.notifySeller("ban")
        self.notifyBidders("ban")

    def getTitle(self):
        temp = self.title
        return temp

    def setWinner(self, winner):
        self.winner = winner

    def getWinner(self):
        temp = self.winner
        return temp

    def notifyBidders(self, reason):
        # If ban notifies all bidders
        if reason == "ban":
            from_email = settings.EMAIL_HOST_USER
            to_email = [from_email]
            for p in self.bidders:
                to_email.append(userInfo.getEmail(p))

            send_mail(subject="Auction banned",
                      message="The admin has banned this auction: %s" % self.getTitle(),
                      from_email=from_email, recipient_list=to_email, fail_silently=False, )

        elif reason == "resolved":
            from_email = settings.EMAIL_HOST_USER
            to_email = [from_email]
            for p in self.bidders:
                if p != self.winner:
                    to_email.append(userInfo.getEmail(p))

            send_mail(subject="Auction resolved",
                      message="The auction %s has been resolved" % self.getTitle(),
                      from_email=from_email, recipient_list=to_email, fail_silently=False, )

    def resolveAuction(self):
        self.is_active = False
        self.notifySeller("resolved")
        if self.winner is not None and self.bidders is not None:
            self.notifyWinner("resolved")
            self.notifyBidders("resolved")

    def notifySeller(self, reason):
        if reason == "newbid":
            from_email = settings.EMAIL_HOST_USER
            self.seller.email
            to_email = [from_email, self.seller.email]
            send_mail(subject="New bid on auction",
                      message="A new bid was placed on your auction: %s" % self.getTitle(),
                      from_email=from_email, recipient_list=to_email, fail_silently=False, )

        elif reason == "ban":
            from_email = settings.EMAIL_HOST_USER
            to_email = [from_email, self.seller.email]
            send_mail(subject="Auction banned",
                      message="The admin has banned your auction: %s" % self.getTitle(),
                      from_email=from_email, recipient_list=to_email, fail_silently=False, )

        elif reason == "resolved":
            from_email = settings.EMAIL_HOST_USER
            to_email = [from_email, self.seller.email]
            send_mail(subject="Auction resolved",
                      message="The following auction has been resolved: %s" % self.getTitle(),
                      from_email=from_email, recipient_list=to_email, fail_silently=False, )

    def notifyWinner(self, reason):
        if reason == "newbid":
            from_email = settings.EMAIL_HOST_USER
            to_email = [from_email, userInfo.getEmail(self.winner)]
            send_mail(subject="Bid received on auction", message="Your bid was successfully placed on auction: %s"
                                                                 % self.getTitle(),
                      from_email=from_email, recipient_list=to_email, fail_silently=False, )

        elif reason == "resolved":
            from_email = settings.EMAIL_HOST_USER
            to_email = [from_email, userInfo.getEmail(self.winner)]
            send_mail(subject="Auction resolved", message="Congratulations you have won the auction: %s"
                                                          % self.getTitle(),
                      from_email=from_email, recipient_list=to_email, fail_silently=False, )
