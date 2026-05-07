"""
URL Configuration for Skills App
=================================
Maps URLs to views

Pattern: URL path → View function
Example: /skills/ → skill_list_view
"""

from django.urls import path
from . import views

urlpatterns = [
    # ============================================================
    #  AUTHENTICATION URLs
    # ============================================================
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    
    # ============================================================
    #  HOME & DASHBOARD
    # ============================================================
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    
    # ============================================================
    #  SKILL URLs (Main CRUD operations)
    # ============================================================
    path('skills/', views.skill_list_view, name='skill_list'),
    path('skills/<int:pk>/', views.skill_detail_view, name='skill_detail'),
    path('skills/create/', views.skill_create_view, name='skill_create'),
    path('skills/<int:pk>/edit/', views.skill_update_view, name='skill_update'),
    path('skills/<int:pk>/delete/', views.skill_delete_view, name='skill_delete'),
    
    
    # ============================================================
    #  REVIEW URLs
    # ============================================================
    path('skills/<int:skill_pk>/review/', views.add_review_view, name='add_review'),
    
    
    # ============================================================
    #  BOOKING REQUEST URLs
    # ============================================================
    path('skills/<int:skill_pk>/book/', views.create_booking_request_view, name='create_booking'),
    path('bookings/my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('bookings/incoming/', views.incoming_bookings_view, name='incoming_bookings'),
    path('bookings/<int:booking_pk>/manage/', views.manage_booking_request_view, name='manage_booking'),
    path('bookings/<int:booking_pk>/cancel/', views.cancel_booking_view, name='cancel_booking'),
    
    
    # ============================================================
    #  PROFILE URLs
    # ============================================================
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    
    
    # ============================================================
    #  SEARCH URL
    # ============================================================
    path('search/', views.search_view, name='search'),
]
