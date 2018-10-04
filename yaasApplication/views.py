from django.shortcuts import render
from django.http import HttpResponse
from .models import auction
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from yaasApplication.forms import UserCreationForm, changeEmailForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect




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








