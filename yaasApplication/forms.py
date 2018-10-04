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

    #Write CleanData method?

    #class Meta:
      #  model = User
    #   fields = "New email"

   # def __init__(self, user, *args, **kwargs):
   #     self.user = user
   #     super().__init__(*args, **kwargs)


  #  def save_all_files(self, commit=True):
   #     email =
   #     self.user.set_email(email)
   #     if commit:
    #        self.user.save_all_files()
    #    return self.user
