from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from yaasApplication.models import auction
from django.conf import settings



class UserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    language = forms.ChoiceField(choices=settings.LANGUAGES, required=True)
    lang = ""

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "language")

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.language = self.cleaned_data["language"]
        self.lang = self.cleaned_data["language"]
        print(self.cleaned_data["language"])
        print("Saved")
        if commit:
            user.save()
        return user


    def getName(self):
        return self.username

    def getLang(self):
        return self.lang


class changeEmailForm(forms.Form):
    new_email = forms.EmailField(label="Email", required=True)

class auctionForm(forms.Form):
    class Meta:
        model = User
        fields = ("title", "description", "minprice", "deadline")

    title = forms.CharField(max_length=30)
    description = forms.CharField(max_length=300, widget=forms.Textarea)
    minprice = forms.IntegerField()
    deadline = forms.DateTimeField()


class bidForm(forms.Form):
    bid = forms.DecimalField()


class editDescriptionForm(forms.Form):
    description = forms.CharField(max_length=300, widget=forms.Textarea)

    class Meta:
        model = auction
        fields = ('description')
