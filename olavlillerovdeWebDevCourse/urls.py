"""olavlillerovdeWebDevCourse URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from yaasApplication.views import home, register, change_password, change_email, create_auction, edit_auction, my_auctions, \
    search_auction, place_bid, banAuction, banned_auctions, loginuser, lougoutuser
from django.conf.urls import url

from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView


urlpatterns = [
    url(r'^$', home, name="index"),
    url(r'admin/', admin.site.urls),
    url(r'^login', loginuser, name="login"),
    url(r'^logout', lougoutuser, name="logout"),
    #path('accounts/', include('django.contrib.auth.urls')),
    url(r'register/', register, name="register"),
    url(r'^password/$', change_password, name='change_password'),
    url(r'^email/$', change_email, name='change_email'),
    url(r'^create_auction', create_auction, name='create_auction'),
    url(r'^edit_auction/(?P<id>.*)', edit_auction, name='edit_auction'),
    url(r'^my_auctions', my_auctions, name="my_auctions"),
    url(r'^search_auction=$', search_auction, name="search_auction"),
    url(r'^place_bid/(?P<id>.*)', place_bid, name="place_bid"),
    url(r'^ban_auction/(?P<id>.*)', banAuction, name='ban_auction'),
    url(r'^banned auctions', banned_auctions, name='banned_auctions'),
    path('i18n/', include('django.conf.urls.i18n')),
]
