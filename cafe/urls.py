from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('wait/', views.wait, name="wait"),
    path('contact/', views.contact, name="contact"),
]
