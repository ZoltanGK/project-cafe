from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from cafe.models import Contact, Issue, Response

class ContactForm(forms.ModelForm):
    name = forms.CharField(max_length=64, required=False, label="Name (optional)")
    issue = forms.CharField(label = "Submit Issue", max_length = 1024, widget=forms.Textarea)

    class Meta:
        model = Contact
        fields = ('name', 'issue',)

class IssueForm(forms.ModelForm):
    title = forms.CharField(max_length=64, required=True,  label="Title")
    content = forms.CharField(label = "Type out your Issue", max_length=1024, widget=forms.Textarea)
    anonymous = forms.BooleanField(label = "Anonymous?", required=False)

    class Meta:
        model = Issue
        fields = ('title', 'content', 'anonymous',)

class UserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ("email", "username", "password1", "password2")

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class ResponseForm(forms.ModelForm):
    content = forms.CharField(label = "Type out your response", max_length=1024, widget=forms.Textarea)

    class Meta:
        model = Issue
        fields = ('content',)