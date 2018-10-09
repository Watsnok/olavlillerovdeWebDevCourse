from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
from django import forms

# Create your models here.

class auction(models.Model):
    title = models.CharField(max_length=30)
    seller = models.ForeignKey(User, related_name="auctions", on_delete=models.CASCADE)
    description = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    minprice = models.IntegerField()
    deadline = models.DateTimeField()

    def __str__(self):
        return self.title

    def checkDeadline(self, created, deadline):
        duration = datetime.timedelta(days=3)
        diff = deadline - duration
        if (diff.year < created.year) or (diff.year == created.year and diff.month == created.month
                                          and diff.day <= created.day) or (diff.year == created.year
                                                                             and diff.month < created.month):
            raise forms.ValidationError("Duration must be longer than 72 hours")
        else:
            return True
