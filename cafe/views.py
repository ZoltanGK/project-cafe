from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from cafe.forms import ContactForm

def index(request):
	return render(request, 'cafe/index.html')

def wait(request):
	return render(request, 'cafe/wait.html')

def register(request):
	if request.method == 'POST':
		form = UserCreationForm(request.POST)

		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			user = authenticate(username=username, password=password)
			login(request, user)
			return redirect('index')
	else:
		form = UserCreationForm()



	context = {'form' : form}
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
	return render(request, 'cafe/contact.html', {'form' : form})
    


def student_account(request):
    
    if request.method == 'POST':
        pass
        # student is submitting a new issue
        # read the form and create a new issue
    # no context dict needed
    return render(request, 'cafe/student-account.html')
    

def view_queries(request):   
    if request.method == 'POST':
        pass
        #the student is replying to an issue
        #create the new reply
    # get all issues for that student 
    # get all responses for each issue
    context_dict = {}
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
    return render(request, 'cafe/view_queries.html', context_dict)
    

def staff_account(request):
    # get all issues for that staff in the same format as the dictionary from view_queries view
    context_dict = {}

    return render(request, 'cafe/staff_account.html', context_dict)
    
def create_response(request):
    if request.method == 'POST':
        pass
        #the staff is replying to an issue
        #create the new reply
    # get all issues for that staff in the same format as the dictionary from view_queries view
    context_dict = {}
    return render(request, 'cafe/create_response.html', context_dict)
        