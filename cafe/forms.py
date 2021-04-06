from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms.widgets import CheckboxSelectMultiple
from cafe.models import Contact, Issue, Response, Category

class ContactForm(forms.ModelForm):
    name = forms.CharField(max_length=64, required=False, label="Name (optional)")
    issue = forms.CharField(label = "Submit Issue", max_length = 1024, widget=forms.Textarea)

    class Meta:
        model = Contact
        fields = ('name', 'issue',)

class IssueForm(forms.ModelForm):
    title = forms.CharField(max_length=64, required=True,  label="Title")
    categories = forms.ModelMultipleChoiceField(Category.objects.all(), label = "Please select relevant categories", widget=CheckboxSelectMultiple)
    content = forms.CharField(label = "Type out your Issue", max_length=1024, widget=forms.Textarea)
    anonymous = forms.BooleanField(label = "Anonymous?", required=False)

    class Meta:
        model = Issue
        fields = ('title', 'categories', 'content', 'anonymous',)

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
    # Allows for submission of a reply to a given issue
    # Issue information is passed in request.POST
    content = forms.CharField(label = "Type out your response", max_length=1024, widget=forms.Textarea)

    class Meta:
        model = Response
        fields = ('content',)

class StudentResponseForm(forms.ModelForm):
    # Student version of ResponseForm that allows for anonymous replies
    content = forms.CharField(label = "Type out your response", max_length=1024, widget=forms.Textarea)
    anonymous = forms.BooleanField(label = "Anonymous?", required=False)

    class Meta:
        model = Response
        fields = ('content','anonymous',)