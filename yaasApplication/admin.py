from django.contrib import admin
from .models import auction, user

admin.site.register(user)
admin.site.register(auction)