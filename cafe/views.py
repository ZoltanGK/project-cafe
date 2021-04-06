import urllib
import json
import datetime
import requests
from django.shortcuts import render, redirect
from .forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from cafe.forms import ContactForm, IssueForm, ResponseForm, StudentResponseForm
from django.conf import settings
from django.contrib import messages
from cafe.models import Student, Staff, Issue, Response, UserProfile
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

def index(request):
	return render(request, 'cafe/index.html', {'user_info': user_info_dict(request)})

def wait(request):
    user_type = get_user_type(request)
    # If user is not Unassigned, then redirect them to their own login page
    if user_type != "Unassigned":
        return redirect_to_correct_page(user_type)
    return render(request, 'cafe/wait.html', {'user_info': user_info_dict(request)})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Garg, A (2020) Add reCAPTCHA In Your Django App 
            # [Source code]. https://studygyaan.com/django/add-recaptcha-in-your-django-app-increase-security
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
    # Contact form that creates a Contact object that admins can view.
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
    # make sure only students access this view
    user_type = get_user_type(request)
    if user_type != "Student":
        #redirect non-students to their own page
        return redirect_to_correct_page(user_type)
    
    form = IssueForm()
    if request.method=='POST':
        form = IssueForm(request.POST)

        if form.is_valid():
            issue = form.save()
            # Form didn't contain user info, so add that here
            issue.poster = Student.objects.get(user = request.user)
            issue.save()
            return redirect('thank_you')
        else:
            print(form.errors)
    return render(request, 'cafe/student_account.html', {'form' : form, 'user_info': user_info_dict(request)})

@login_required
def thank_you(request):
    user_type = get_user_type(request)
    if user_type != "Student":
        return redirect_to_correct_page(user_type)
    return render(request, 'cafe/thank_you.html', {'user_info': user_info_dict(request)})
    
@login_required    
def staff_thank_you(request):
    user_type = get_user_type(request)
    if user_type != "Staff":
        return redirect_to_correct_page(user_type)
    return render(request, 'cafe/staff_thank_you.html', {'user_info': user_info_dict(request)})

@login_required
def view_queries(request): 
    # make sure only students access this view
    user_type = get_user_type(request)
    if user_type != "Student":
        #redirect non-students to their own page
        return redirect_to_correct_page(user_type)
    
    form = StudentResponseForm()

    if request.method == 'POST':
        # We need to find the id of the issue the response is to
        # This info is contained in the name of the submit input
        # That name is a key in request.POST
        post_keys = list(request.POST.dict().keys())
        # We know the corresponding value ("Post Reply"), so we find that first,
        # then use that to find the name.
        post_vals = list(request.POST.values())
        response_ix = post_vals.index("Post Reply")
        # Name is of the format "response_for_issue_id" and we need only the
        # issue_id
        issue_id = post_keys[response_ix][13:]

        form = StudentResponseForm(request.POST)

        if form.is_valid():
            response = form.save(commit=False)
            response.issue = Issue.objects.get(id = issue_id)
            response.poster = UserProfile.objects.get(user = request.user)
            response.save()
            return redirect('view_queries')
        else:
            print(form.errors)
    context_dict = get_context_dict_student(request)
    return render(request, 'cafe/view_queries.html', context = {'issue' : context_dict, 'form' : form ,'user_info': user_info_dict(request)})
    
@login_required
def staff_account(request):
    # make sure only staff access this view
    user_type = get_user_type(request)
    if user_type != "Staff":
        #redirect non-staff to their own page
        return redirect_to_correct_page(user_type)
    
    form = ResponseForm()

    if request.method == 'POST':
        # We need to find the id of the issue the response is to
        # This info is contained in the name of the submit input
        # That name is a key in request.POST
        post_keys = list(request.POST.dict().keys())
        # We know the corresponding value ("Post Reply"), so we find that first,
        # then use that to find the name.
        post_vals = list(request.POST.values())
        response_ix = post_vals.index("Post Reply")
        # Name is of the format "response_for_issue_id" and we need only the
        # issue_id
        issue_id = post_keys[response_ix][13:]

        form = ResponseForm(request.POST)

        if form.is_valid():
            response = form.save(commit=False)
            response.issue = Issue.objects.get(id = issue_id)
            response.poster = UserProfile.objects.get(user = request.user)
            response.save()
            return redirect('staff_thank_you')
        else:
            print(form.errors)
    context_dict = get_context_dict_staff(request)
    return render(request, 'cafe/staff_account.html', context = {'issue' : context_dict, 'form' : form, 'user_info': user_info_dict(request)})

   
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
            if user:
                login(request, user)
                if Staff.objects.filter(user = user):
                    return redirect('staff_account')
                elif Student.objects.filter(user = user):
                    return redirect('student_account')
                else:
                    return redirect('index')
            else:
                return HttpResponse("Invalid login details supplied.")
        else:
            # If the captcha is failed redirect back to login page
            # so the user can try again.
            messages.error(request,"Invalid Captcha Try Again")
            return redirect('/doLogin')
    else:
        messages.error(request, 'Invalid reCAPTCHA. Please try again.')
        return redirect('login')

def user_logout(request):
    context = RequestContext(request)
    logout(request)
    # Redirect back to index page.
    return redirect('index')
        
def user_info_dict(request):
    """
    Returns a dictionary of the user's staff/student status and their full name.

    For unauthenticated/unassigned users, returns name as Unknown.
    """
    user = request.user
    if user.is_authenticated:
        # There must be exactly one student/staff object for each user if they have the role
        # So if we find none, then the user isn't a staff/student
        is_student = len(Student.objects.filter(user = user)) > 0
        is_staff = len(Staff.objects.filter(user = user)) > 0
        # We expect the userprofile to exist and contain the user's full name
        if UserProfile.objects.filter(user=user):
            name = UserProfile.objects.get(user=user).name
        else:
            name = "Unknown"
        return {"is_student": is_student, "is_staff": is_staff, "name": name}
    else:
        return {"is_student": False, "is_staff": False, "name": "Unknown"}
        
#helper fn to get the context dict for student views
def get_context_dict_student(request):
    user = request.user
    user_student = Student.objects.get(user=user)
    # Find all posts by user and order them by newest first
    # Date here is redundant as newer objects have higher IDs, but this should 
    # be helpful for futureproofing
    issues = Issue.objects.filter(poster = user_student).order_by('-date', '-id')
    context_dict = generate_context_dict(request, issues)
    return context_dict
 
#helper fn to get the context dict for staff views 
def get_context_dict_staff(request):
    #context_dict format is the same as for students 
    user = request.user
    user_staff = Staff.objects.get(user=user)
    #categories assigned to that user
    user_categories = user_staff.get_cats_resp()
    # combine all the issues in said categories
    issues = user_categories[0].issues
    for cat in user_categories:
        issues = issues.union(cat.issues)
    issues.order_by('-date', '-id')
    context_dict = generate_context_dict(request, issues)
    return context_dict
    
def generate_context_dict(request, issues):
    """
    context_dict is a dictionary of all issues and replies of the format: 
    {'issue id':{'title': title, 
                  'date': date, 
                  'anonymous': anonymous, 
                  'poster': poster,
                  'content': content 
                  'categories' : categories,
                  'num_categories' : len(categories),
                  'status' : status,
                  'responses':[{'number': number, 'date':date, 'content':content, 'poster': poster, 'anonymous': anonymous}]
                  }
    """
    context_dict = {}
    for issue in issues:
        issue_poster = UserProfile.objects.get(user = issue.poster.user).name
        responses = []
        num_categories = issue.categories.all().count()
        for response in Response.objects.filter(issue = issue).order_by('number'):
            response_poster = UserProfile.objects.get(user = response.poster.user).name
            dict_response = {'number' : response.number, 'date': response.date, 
                             'content': response.content, 'poster': response_poster,
                             'anonymous': response.anonymous}
            responses.append(dict(dict_response))
        context_dict[issue.id] = { 
                    'title': issue.title,
                    'date': issue.date, 
                    'anonymous': issue.anonymous, 
                    'poster': issue_poster,
                    'content': issue.content,
                    'categories' : issue.in_categories(),
                    'num_categories' : num_categories,
                    'status' : issue.status,
                    'responses': responses
                    }
    return context_dict
    
#helper fn to get the type of user making the request (staff/student/unassigned)
def get_user_type(request):
    if len(Student.objects.filter(user = request.user))>0:
        return "Student"
    elif len(Staff.objects.filter(user = request.user))>0:
        return "Staff"
    else:
        return "Unassigned"
        
#helper fn to redirect a user from a page they are not authorised to access (such as staff accessing a student view)
def redirect_to_correct_page(user_type):
    if user_type == "Staff":
        return redirect('staff_account')
    elif user_type == "Student":
        return redirect('student_account')
    else:
        return redirect('wait')
