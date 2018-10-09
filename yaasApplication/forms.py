from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms


class UserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


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

