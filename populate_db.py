import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE",
"project_cafe.settings")

import django
django.setup()
from django.contrib.auth.models import User, Permission
from django.contrib.auth.hashers import make_password
from cafe.models import Category, UserProfile, Staff, Student, Issue, Response, Contact
from datetime import date

default_pw = "@dmin123"

def populate():

    users = {"jsmith": {"name": "Jane Smith", 
                        "email": "jsmith@example.gla.ac.uk",
                        "staff": True, 
                        "role": "Level 1 Tutor Representative",
                        "student": False,
                        "courses": "COMPSCI5059, COMPSCI5092",
                        "lab_groups": ""},
             "jhw":     {"name": "John Williamson", 
                        "email": "jhw@example.gla.ac.uk",
                        "staff": True, 
                        "role": "Lecturer",
                        "student": False,
                        "courses": "",
                        "lab_groups": ""},
             "mef":     {"name": "Mary Ellen Foster", 
                        "email": "mef@example.gla.ac.uk",
                        "staff": True, 
                        "role": "Director of Learning and Teaching",
                        "student": False,
                        "courses": "",
                        "lab_groups": ""},
            "zgk":      {"name": "Zoltan Kiss", 
                        "email": "zgk15@example.gla.ac.uk",
                        "staff": False, 
                        "role": "",
                        "student": True,
                        "courses": "COMPSCI2008, COMPSCI2007, COMPSCI2021",
                        "lab_groups": "LB02, LB09, LB13"},
            "ay":      {"name": "Anon Ymous", 
                        "email": "anony@example.gla.ac.uk",
                        "staff": False, 
                        "role": "",
                        "student": True,
                        "courses": "COMPSCI1001, COMPSCI1018, COMPSCI1006",
                        "lab_groups": "LB15, LB01, LB06"},
            "nouser":  {"name": "Not a User", 
                        "email": "notAuser@example.gla.ac.uk",
                        "staff": False, 
                        "role": "",
                        "student": False,
                        "courses": "",
                        "lab_groups": ""},

    }
    # Key = Category Name, Value = List of responsible staff
    categories = {"CS1P Feedback": ["jhw", "mef"],
                  "Online Learning Feedback": ["mef"],
                  "General Tutor Feedback": ["jsmith", "mef"],
                  "Test Category": ["jhw", "jsmith"]}

    issues = [{"categories": ["Test Category", "General Tutor Feedback"], 
               "poster": "zgk", 
               "anonymous": True, 
               "status": 1, 
               "title": "Test Issue 1",
               "content": "This is test issue 1. Anonymous."},
              {"categories": ["Test Category", "Online Learning Feedback"], 
               "poster": "zgk", 
               "anonymous": False, 
               "status": 0, 
               "title": "Test Issue 2",
               "content": "This is test issue 2. Not Anonymous."}, 
              {"categories": ["CS1P Feedback", "Test Category"], 
               "poster": "ay", 
               "anonymous": True, 
               "status": 2, 
               "title": "Anonymous More Cooper",
               "content": "CS1P needs more Cooper! - Anonymous."}, 
              {"categories": ["CS1P Feedback", "Test Category"], 
               "poster": "ay", 
               "anonymous": False, 
               "status": 0, 
               "title": "Named More Cooper",
               "content": "CS1P needs more Cooper! - Anon Ymous."}, 
              {"categories": ["Online Learning Feedback"], 
               "poster": "zgk", 
               "anonymous": False, 
               "status": 0, 
               "title": "Ups and Downs", 
               "content": "I think online learning has had both negative and positive aspects."}, 
              {"categories": ["General Tutor Feedback", "CS1P Feedback"], 
               "poster": "zgk", 
               "anonymous": False, 
               "status": 0, 
               "title": "CS1P Semester 1 Tutor feedback", 
               "content": "While my tutor wasn't present much for CS1P, they were very helpful!"},]

    responses = [{"id": 3, "poster": "jhw", "content": "That depends on the [Cooper]ation of the animal involved."},
                 {"id": 3, "poster": "ay", "anonymous": True, "content": "Hahaha, naturally. Thank you!"},
                 {"id": 1, "poster": "jsmith", "content": "Thank you for test issue 1. This is reply 1."},]

    print("\n--Creating Users--")
    for username, user_params in users.items():
        add_user(username, user_params)
        print(f"Added: {username}")

    print("\n--Creating Categories--")
    for cat_name, cat_staff in categories.items():
        add_category(cat_name, cat_staff)
        print(f"Added: {cat_name}")

    print("\n--Creating Issues--")
    i = 0
    for issue_dict in issues:
        add_issue(**issue_dict)
        print(f"Added: Issue #{i}")
        i += 1

    print("\n--Creating Responses--")
    i = 0
    for resp_dict in responses:
        add_response(**resp_dict)
        print(f"Added: Response #{i} to Issue #{resp_dict['id']}")
        i += 1

def add_user(username, user_dict, pw = default_pw):
    user = User.objects.get_or_create(username = username)[0]
    user.email = user_dict["email"]
    user.password = make_password(pw)
    user.save()
    user_profile = UserProfile.objects.get_or_create(user=user)[0]
    user_profile.name = user_dict["name"]
    user_profile.email = user_dict["email"]
    user_profile.save()
    if user_dict["student"]:
        student = Student.objects.get_or_create(user=user)[0]
        student.courses = user_dict["courses"]
        student.lab_groups = user_dict["lab_groups"]
        student.save()
    if user_dict["staff"]:
        staff = Staff.objects.get_or_create(user=user)[0]
        staff.role = user_dict["role"]
        staff.save()
    return user

def add_category(name, resp_staff):
    cat = Category.objects.get_or_create(name=name)[0]
    for i in resp_staff:
        user = User.objects.get(username = i)
        permission = Permission.objects.get(codename = f"resp-for-{cat.slug}")
        user.user_permissions.add(permission)
        user.save()
    return cat

def add_issue(categories, poster, anonymous, status, title, content):
    issue = Issue.objects.get_or_create(content = content)[0]
    for cat in categories:
        c = Category.objects.get(name=cat)
        issue.categories.add(c)
    issue.poster = Student.objects.get(user = User.objects.get(username = poster))
    issue.anonymous = anonymous
    issue.status = status
    issue.title = title
    issue.save()
    return issue

def add_response(id, poster, content, anonymous = False):
    issue = Issue.objects.get(id = id)
    resp = Response.objects.get_or_create(issue = issue, content = content)[0]
    resp.issue = issue
    resp.poster = UserProfile.objects.get(user = User.objects.get(username = poster))
    resp.anonymous = anonymous
    resp.save()
    return resp


if __name__ == "__main__":
    print("==Populating Database==")
    populate()
    print("\n==Population Done==")