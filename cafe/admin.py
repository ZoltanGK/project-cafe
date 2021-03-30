from django.contrib import admin
from django.contrib.auth.models import Permission
from cafe.models import Category, UserProfile, Staff, Student, Issue, Response

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class IssueAdmin(admin.ModelAdmin):
    list_display = ("id", "poster", "content", "status", "date")

admin.site.register(UserProfile)
admin.site.register(Staff)
admin.site.register(Student)
admin.site.register(Response)
admin.site.register(Category,  CategoryAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Permission)