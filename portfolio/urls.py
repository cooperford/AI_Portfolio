from django.urls import path

from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('projects/', views.projects, name='projects'),
    path('projects/langchain-chatbot/app/', views.langchain_chatbot, name='langchain_chatbot'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail'),
    path('skills/', views.skills, name='skills'),
    path('resume/', views.resume, name='resume'),
    path('contact/', views.contact, name='contact'),
]
