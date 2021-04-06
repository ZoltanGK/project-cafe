from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('wait/', views.wait, name="wait"),
    path('contact/', views.contact, name="contact"),
    path('login/', views.login, name='login'),
    path('login/student-account/', views.student_account, name='student_account'),
    path('login/student-account/view-queries/', views.view_queries, name='view_queries'),
    path('login/student-account/thank-you/', views.thank_you, name='thank_you'),
    path('login/staff-account/', views.staff_account, name='staff_account'),
    path('login/staff-account/thank-you/', views.staff_thank_you, name='staff_thank_you'),
    path('logout/', views.user_logout, name='logout_screen'),
]
