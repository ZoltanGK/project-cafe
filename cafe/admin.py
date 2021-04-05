from django.contrib import admin
from django.contrib.auth.models import Permission
from cafe.models import Category, UserProfile, Staff, Student, Issue, Response, Contact

def user(obj):
    return obj.user

def name(obj):
    return UserProfile.objects.get(user = obj.user).name

def email(obj):
    return UserProfile.objects.get(user = obj.user).email

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "email")

class StaffAdmin(admin.ModelAdmin):
    list_display = (user, name, "role", email)

class StudentAdmin(admin.ModelAdmin):
    list_display = (user, name, "courses", "lab_groups", email)

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',),}
    list_display = ("name", "issues")

class IssueAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "in_categories", "poster", "status", "date", "content")

class ResponseAdmin(admin.ModelAdmin):
    list_display = ("issue", "number", "anonymous", "poster", "date", "content")

class ContactAdmin(admin.ModelAdmin):
    list_display = ("date", "issue")

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Staff, StaffAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Response, ResponseAdmin)
admin.site.register(Category,  CategoryAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Permission)