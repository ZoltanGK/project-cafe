import urllib
import json
import datetime
import requests
from django.shortcuts import render, redirect
from .forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from cafe.forms import ContactForm, IssueForm, ResponseForm
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from cafe.models import Student, Staff, Issue, Response, UserProfile
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

def index(request):
	return render(request, 'cafe/index.html', {'user_info': user_info_dict(request)})

def wait(request):
	return render(request, 'cafe/wait.html', {'user_info': user_info_dict(request)})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        print(form.is_valid())
        if form.is_valid():
            # Checks to see if captcha was passed
            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            cap_secret="6LfOhpkaAAAAABVLBsLiHM2j8mak-1fQrqz-spSY"
            values = {
                'secret': cap_secret,
                'response': recaptcha_response
                }
            cap_server_response=requests.post(url= url, data=values)
            cap_json=json.loads(cap_server_response.text)

            # If the captcha is passed and the fields are filled out correctly:
            # create a new user, login and go to the home page.
            if cap_json['success']:
                form.save()
                username = form.cleaned_data['username']
                password = form.cleaned_data['password1']
                email = form.cleaned_data['email']
                user = authenticate(username=username, password=password, email=email)
                login(request, user)
                return redirect('/wait')
            else:
                # If the captcha is failed redirect back to register page
                # so the user can try again.
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')
                return redirect('/register')
    else:
        form = UserCreationForm()
    context = {'form' : form, 'user_info': user_info_dict(request)}
    return render(request, 'registration/register.html', context)

def contact(request):
	form = ContactForm()
	
	if request.method =='POST':
		form = ContactForm(request.POST)

		if form.is_valid():
			form.save(commit=True)
			return redirect('index')
		else:
			print(form.errors)
	return render(request, 'cafe/contact.html', {'form' : form, 'user_info': user_info_dict(request)})
    

@login_required
def student_account(request):
    form = IssueForm()

    if request.method=='POST':
        form = IssueForm(request.POST)

        if form.is_valid():
            form.poster = request.user.is_authenticated
            form.date = datetime.date.today()
            form.save(commit=True)
            return redirect('thank_you')
        else:
            print(form.errors)
    return render(request, 'cafe/student_account.html', {'form' : form, 'user_info': user_info_dict(request)})

@login_required
def thank_you(request):
    return render(request, 'cafe/thank_you.html', {'user_info': user_info_dict(request)})
    
@login_required    
def staff_thank_you(request):
    return render(request, 'cafe/staff_thank_you.html', {'user_info': user_info_dict(request)})

@login_required
def view_queries(request):   
    if request.method == 'POST':
        pass
        #the student is replying to an issue
        #create the new reply
    # get all issues for that student 
    # get all responses for each issue
    context_dict = get_context_dict_student(request)
    print(context_dict)
    return render(request, 'cafe/view_queries.html', context = {'issue' : context_dict, 'user_info': user_info_dict(request)})
    
@login_required
def staff_account(request):
    context_dict = get_context_dict_staff(request)
    return render(request, 'cafe/staff_account.html', context = {'issue' : context_dict, 'user_info': user_info_dict(request)})

@login_required    
def create_response(request):
    form = ResponseForm()

    if request.method == 'POST':
        form = ResponseForm(request.POST)

        if form.is_valid():
            if Issue:
                response = form.save(commit=False)
                response.Issue = Issue
                response.date = datetime.date.today()
                response.poster = UserProfile.objects.get(user = request.user)
                response.save()
            return redirect('staff_thank_you')
        else:
            print(form.errors)
    context_dict = get_context_dict_staff(request)
    return render(request, 'cafe/create_response.html', context = {'issue' : context_dict, 'form' : form, 'user_info': user_info_dict(request)})
    
#helper fn to get the context dict for student views
def get_context_dict_student(request):
    #context_dict is a dictionary of all issues and replies of the format: 
    # {'issue id':{'title': title, 
    #               'date': date, 
    #               'anonymous': anonymous, 
    #               'poster': poster,
    #               'content': content 
    #               'categories' : categories,
    #               'status' : status,
    #               'responses':[{'number': number, 'date':date, 'content':content, 'poster': poster}]
    #               }
    user = request.user
    user_student = Student.objects.get(user=user)
    issues = Issue.objects.filter(poster = user_student)
    context_dict = {}
    for issue in issues:
        categories = []
        responses = []
        for category in issue.categories.all():
            categories.append(category.name)
        for response in Response.objects.filter(issue = issue).order_by('number'):
            response_poster = UserProfile.objects.get(user = response.poster.user).name
            dict_response = {'number' : response.number, 'date': response.date, 'content': response.content, 'poster': response_poster}
            responses.append(dict(dict_response))
        context_dict[issue.id] = { 
                    'title': issue.title,
                    'date': issue.date, 
                    'anonymous': issue.anonymous, 
                    'poster': UserProfile.objects.get(user = user).name,
                    'content': issue.content,
                    'categories' : issue.in_categories(),
                    'status' : issue.status,
                    'responses': responses
                    }
    return context_dict
 
#helper fn to get the context dict for staff views 
def get_context_dict_staff(request):
    #context_dict format is the same as for students:    
    user = request.user
    user_staff = Staff.objects.get(user=user)
    #categories assigned to that user
    user_categories = user_staff.get_cats_resp()
    issues = []
    for category in user_categories:
        # get all issues for that category
        cat_issues = category.issues
        # this is to prevent duplicates in the issues list
        for cat_issue in cat_issues:
            if cat_issue not in issues:
                issues.append(cat_issue)
        
    context_dict = {}
    for issue in issues:
        issue_poster = UserProfile.objects.get(user = issue.poster.user).name
        categories = []
        responses = []
        for category in issue.categories.all():
            categories.append(category.name)
        for response in Response.objects.filter(issue = issue).order_by('number'):
            response_poster = UserProfile.objects.get(user = response.poster.user).name
            dict_response = {'number' : response.number, 'date': response.date, 'content': response.content, 'poster': response_poster}
            responses.append(dict(dict_response))
        context_dict[issue.id] = { 
                    'title': issue.title,
                    'date': issue.date, 
                    'anonymous': issue.anonymous, 
                    'poster': issue_poster,
                    'content': issue.content,
                    'categories' : issue.in_categories(),
                    'status' : issue.status,
                    'responses': responses
                    }
    print(context_dict)
    return context_dict

def doLogin(request):
    if request.method=="POST":
        # Checks to see if captcha was passed
        recaptcha_response = request.POST.get('g-recaptcha-response')
        url = 'https://www.google.com/recaptcha/api/siteverify'
        cap_secret="6LfOhpkaAAAAABVLBsLiHM2j8mak-1fQrqz-spSY"
        values = {
            'secret': cap_secret,
            'response': recaptcha_response
            }
        cap_server_response=requests.post(url= url, data=values)
        cap_json=json.loads(cap_server_response.text)

        # If the captcha is passed and the fields are filled out correctly:
        # login and go to the home page.
        if cap_json['success']==True:
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(username=username, password=password)
            login(request, user)
            if Staff.objects.filter(user = user):
                return redirect('staff_account')
            elif Student.objects.filter(user = user):
                return redirect('student_account')
            else:
                return redirect('wait')
        else:
            # If the captcha is failed redirect back to login page
            # so the user can try again.
            messages.error(request,"Invalid Captcha Try Again")
            return redirect("/doLogin")
    else:
        messages.error(request, 'Invalid reCAPTCHA. Please try again.')
        return redirect('/accounts/login/')

def user_logout(request):
    context = RequestContext(request)
    logout(request)
    # Redirect back to index page.
    return redirect('index')
        
def user_info_dict(request):
    user = request.user
    if user.is_authenticated:
        is_student = len(Student.objects.filter(user = user)) > 0
        is_staff = len(Staff.objects.filter(user = user)) > 0
        if UserProfile.objects.filter(user=user):
            name = UserProfile.objects.get(user=user).name
        else:
            name = "Unknown"
        return {"is_student": is_student, "is_staff": is_staff, "name": name}
    else:
        return {"is_student": False, "is_staff": False, "name": "Unknown"}