from django.contrib import admin
from django.contrib.auth.models import Permission
from cafe.models import Category, UserProfile, Staff, Student, Issue, Response, Contact

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "email")

class StaffAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "email", "role")

class StudentAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "courses", "lab_groups")

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class IssueAdmin(admin.ModelAdmin):
    list_display = ("id", "poster", "status", "date", "content")

class ResponseAdmin(admin.ModelAdmin):
    list_display = ("issue", "number", "poster", "date", "content")

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