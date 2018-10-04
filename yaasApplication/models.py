from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class auction(models.Model):
    title = models.CharField(max_length=30)
    seller = models.ForeignKey(User, related_name="auctions", on_delete=models.CASCADE)
    description = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    minprice = models.IntegerField()

    def __str__(self):
        return self.title




