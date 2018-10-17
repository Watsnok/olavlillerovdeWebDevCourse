from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
from django import forms
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q



# Create your models here.

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

    def __str__(self):
        return self.title

    def addBidder(self, bidder):
        if bidder not in self.bidders:
            self.bidders.append(bidder)

    def getBidders(self):
        return self.bidders

    def checkDeadline(self, created, deadline):
        duration = datetime.timedelta(days=3)
        diff = deadline - duration
        if (diff.year < created.year) or (diff.year == created.year and diff.month == created.month
                                          and diff.day <= created.day) or (diff.year == created.year
                                                                             and diff.month < created.month):
            #raise forms.ValidationError("Duration must be longer than 72 hours")
            return False
        else:
            return True


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
        if reason=="ban":
            from_email = settings.EMAIL_HOST_USER
            to_email = [from_email]
            for p in self.bidders:
                to_email.append(p)

            send_mail(subject="Auction banned",
                      message="The admin has banned this auction: %s" % self.getTitle(),
                      from_email=from_email, recipient_list=to_email, fail_silently=False, )

        elif reason == "resolved":
            from_email = settings.EMAIL_HOST_USER
            to_email = [from_email]
            for p in self.bidders:
                to_email.append(p)

            send_mail(subject="Auction resolved",
                      message="The auction %s has been resolved" % self.getTitle(),
                      from_email=from_email, recipient_list=to_email, fail_silently=False, )


    def notifySeller(self, reason):
        if reason == "newbid":
            from_email = settings.EMAIL_HOST_USER
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

    def notifyWinner(self, reason):
        if reason == "newbid":
            from_email = settings.EMAIL_HOST_USER
            to_email = [from_email, self.winner.email]
            send_mail(subject="Bid received on auction", message="Your bid was successfully placed on auction: %s"
                                           % self.getTitle(),
                      from_email=from_email, recipient_list=to_email, fail_silently=False, )