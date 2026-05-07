"""
Views for Campus SkillSwap
==========================
These functions handle the logic for each page:
- What data to fetch from database
- How to process that data
- What template to show
- What data to pass to that template
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import Http404
from django.views.decorators.http import require_POST
from datetime import datetime

# Import our models and forms
from .models import Skill, Review, BookingRequest, UserProfile
from .forms import (
    RegisterForm, UserProfileForm, SkillForm, SkillSearchForm,
    ReviewForm, BookingRequestForm, BookingRequestReplyForm
)
from django.contrib.auth.models import User


# ============================================================
#  AUTHENTICATION VIEWS (Login, Register, Logout)
# ============================================================

def register_view(request):
    """
    User registration page - lets new users create accounts
    
    GET: Show the registration form
    POST: Process the submitted form
    """
    if request.user.is_authenticated:
        # If already logged in, redirect to home
        return redirect('home')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Create the user from the form
            user = form.save()
            
            # Create a UserProfile for this new user
            UserProfile.objects.create(user=user)
            
            # Show success message
            messages.success(request, 'Account created! You can now log in.')
            
            # Redirect to login page
            return redirect('login')
        else:
            # Form had errors, show them
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegisterForm()
    
    context = {'form': form}
    return render(request, 'auth/register.html', context)


def login_view(request):
    """
    User login page - authenticates existing users
    
    GET: Show login form
    POST: Check username/password in database
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Try to authenticate the user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login successful!
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            # Login failed
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'auth/login.html')


def logout_view(request):
    """
    User logout - clears the session
    
    This is simple - just log them out and redirect
    """
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


# ============================================================
#  HOME & DASHBOARD VIEWS
# ============================================================

def home_view(request):
    """
    Homepage - shows all available skills and latest posted
    
    Displays:
    - Search form
    - All skills (ordered by newest)
    - Link to post a skill
    """
    # Get all skills, ordered by newest first
    skills = Skill.objects.filter(availability_status='available').order_by('-created_at')[:12]
    
    # Create search form (even if not submitted)
    search_form = SkillSearchForm()
    
    context = {
        'skills': skills,
        'search_form': search_form,
        'total_skills': Skill.objects.count(),
        'total_users': User.objects.count(),
        'total_reviews': Review.objects.count(),
    }
    return render(request, 'home.html', context)


@login_required(login_url='login')
def dashboard_view(request):
    """
    User dashboard - personalized view for logged-in users
    
    Shows:
    - Skills they've posted
    - Booking requests for their skills
    - Bookings they've made
    - Their profile info
    - Option to edit profile
    """
    user = request.user
    
    # Get this user's skills
    my_skills = user.skills.all()
    
    # Get booking requests FOR this user's skills
    incoming_bookings = BookingRequest.objects.filter(
        skill__owner=user
    ).order_by('-created_at')
    
    # Get booking requests FROM this user
    my_bookings = BookingRequest.objects.filter(
        requester=user
    ).order_by('-created_at')
    
    # Get or create their profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    context = {
        'profile': profile,
        'my_skills': my_skills,
        'incoming_bookings': incoming_bookings,
        'my_bookings': my_bookings,
        'skills_count': my_skills.count(),
        'pending_requests': incoming_bookings.filter(status='pending').count(),
        'rating': profile.average_rating,
    }
    return render(request, 'dashboard.html', context)


# ============================================================
#  SKILL VIEWS (List, Detail, Create, Update, Delete)
# ============================================================

def skill_list_view(request):
    """
    Show all skills - main skills marketplace page
    
    Features:
    - List all skills
    - Search by title/description
    - Filter by category
    - Shows rating, price, owner
    """
    skills = Skill.objects.all().order_by('-created_at')
    search_form = SkillSearchForm()
    
    # Handle search
    query = request.GET.get('query', '')
    category = request.GET.get('category', '')
    
    if query:
        # Search in title and description
        skills = skills.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    
    if category:
        # Filter by category
        skills = skills.filter(category=category)
    
    context = {
        'skills': skills,
        'search_form': search_form,
        'query': query,
        'selected_category': category,
    }
    return render(request, 'skills/skill_list.html', context)


def skill_detail_view(request, pk):
    """
    Show details of ONE skill
    
    What to show:
    - Skill title, description, price
    - Who it's from (owner)
    - Reviews/ratings
    - "Book This Skill" button (if not your own)
    - "Edit" button (if you're the owner)
    """
    skill = get_object_or_404(Skill, pk=pk)
    
    # Get reviews for this skill
    reviews = skill.reviews.all().order_by('-created_at')
    
    # Check if current user has already reviewed this
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(reviewer=request.user).first()
    
    context = {
        'skill': skill,
        'reviews': reviews,
        'user_review': user_review,
        'average_rating': skill.average_rating,
        'can_edit': request.user == skill.owner,
        'can_book': request.user.is_authenticated and request.user != skill.owner,
    }
    return render(request, 'skills/skill_detail.html', context)


@login_required(login_url='login')
def skill_create_view(request):
    """
    Create a new skill posting
    
    GET: Show empty form
    POST: Save the new skill to database
    """
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            # Create the skill but don't save yet
            skill = form.save(commit=False)
            
            # Set the owner to current user
            skill.owner = request.user
            
            # Now save it to database
            skill.save()
            
            messages.success(request, 'Skill posted successfully!')
            return redirect('skill_detail', pk=skill.pk)
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = SkillForm()
    
    context = {'form': form, 'title': 'Post a New Skill'}
    return render(request, 'skills/skill_form.html', context)


@login_required(login_url='login')
def skill_update_view(request, pk):
    """
    Edit an existing skill
    
    Security: Only the skill owner can edit it
    """
    skill = get_object_or_404(Skill, pk=pk)
    
    # Check permission: only owner can edit
    if request.user != skill.owner:
        messages.error(request, 'You can only edit your own skills!')
        return redirect('skill_detail', pk=skill.pk)
    
    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Skill updated!')
            return redirect('skill_detail', pk=skill.pk)
    else:
        form = SkillForm(instance=skill)
    
    context = {'form': form, 'skill': skill, 'title': 'Edit Skill'}
    return render(request, 'skills/skill_form.html', context)


@login_required(login_url='login')
def skill_delete_view(request, pk):
    """
    Delete a skill
    
    Security: Only owner can delete
    """
    skill = get_object_or_404(Skill, pk=pk)
    
    if request.user != skill.owner:
        messages.error(request, 'You can only delete your own skills!')
        return redirect('skill_detail', pk=skill.pk)
    
    if request.method == 'POST':
        skill_title = skill.title
        skill.delete()
        messages.success(request, f'Skill "{skill_title}" deleted.')
        return redirect('dashboard')
    
    context = {'skill': skill}
    return render(request, 'skills/skill_confirm_delete.html', context)


# ============================================================
#  REVIEW VIEWS
# ============================================================

@login_required(login_url='login')
def add_review_view(request, skill_pk):
    """
    Add a review/rating to a skill
    
    Rules:
    - Can't review your own skill
    - Can only review if you've made a booking request
    - Can only leave one review per skill per person
    """
    skill = get_object_or_404(Skill, pk=skill_pk)
    
    # Can't review own skill
    if request.user == skill.owner:
        messages.error(request, 'You cannot review your own skill!')
        return redirect('skill_detail', pk=skill.pk)
    
    # Check if user already reviewed this skill
    existing_review = Review.objects.filter(
        skill=skill,
        reviewer=request.user
    ).first()
    
    if request.method == 'POST':
        if existing_review:
            # Update existing review
            form = ReviewForm(request.POST, instance=existing_review)
        else:
            # Create new review
            form = ReviewForm(request.POST)
        
        if form.is_valid():
            review = form.save(commit=False)
            review.skill = skill
            review.reviewer = request.user
            review.save()
            
            messages.success(request, 'Review posted! Thank you for your feedback.')
            return redirect('skill_detail', pk=skill.pk)
    else:
        if existing_review:
            form = ReviewForm(instance=existing_review)
        else:
            form = ReviewForm()
    
    context = {
        'form': form,
        'skill': skill,
        'existing_review': existing_review,
    }
    return render(request, 'reviews/review_form.html', context)


# ============================================================
#  BOOKING REQUEST VIEWS
# ============================================================

@login_required(login_url='login')
def create_booking_request_view(request, skill_pk):
    """
    Request to book a skill session
    
    User fills out when and what they want to learn
    """
    skill = get_object_or_404(Skill, pk=skill_pk)
    
    # Can't book your own skill
    if request.user == skill.owner:
        messages.error(request, 'You cannot book your own skill!')
        return redirect('skill_detail', pk=skill.pk)
    
    if request.method == 'POST':
        form = BookingRequestForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.skill = skill
            booking.requester = request.user
            booking.save()
            
            messages.success(request, 'Booking request sent! Waiting for the skill owner to respond.')
            return redirect('my_bookings')
    else:
        form = BookingRequestForm()
    
    context = {'form': form, 'skill': skill}
    return render(request, 'bookings/booking_form.html', context)


@login_required(login_url='login')
def my_bookings_view(request):
    """
    Show bookings the user has made (sessions they want to attend)
    """
    bookings = BookingRequest.objects.filter(
        requester=request.user
    ).order_by('-created_at')
    
    context = {'bookings': bookings, 'title': 'My Booking Requests'}
    return render(request, 'bookings/booking_list.html', context)


@login_required(login_url='login')
def incoming_bookings_view(request):
    """
    Show booking requests FOR user's skills (people want to learn from them)
    
    They can approve or reject these requests
    """
    bookings = BookingRequest.objects.filter(
        skill__owner=request.user
    ).order_by('-created_at')
    
    context = {'bookings': bookings, 'title': 'Booking Requests For My Skills'}
    return render(request, 'bookings/incoming_bookings.html', context)


@login_required(login_url='login')
def manage_booking_request_view(request, booking_pk):
    """
    Skill owner approves or rejects a booking request
    """
    booking = get_object_or_404(BookingRequest, pk=booking_pk)
    
    # Only the skill owner can manage their bookings
    if request.user != booking.skill.owner:
        messages.error(request, 'You can only manage bookings for your own skills!')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = BookingRequestReplyForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            
            status = booking.status
            if status == 'approved':
                messages.success(request, f'Booking approved for {booking.requester.username}!')
            elif status == 'rejected':
                messages.success(request, f'Booking rejected.')
            
            return redirect('incoming_bookings')
    else:
        form = BookingRequestReplyForm(instance=booking)
    
    context = {'form': form, 'booking': booking}
    return render(request, 'bookings/booking_reply.html', context)


@login_required(login_url='login')
def cancel_booking_view(request, booking_pk):
    """
    Cancel a booking request (for the person who made the request)
    """
    booking = get_object_or_404(BookingRequest, pk=booking_pk)
    
    # Only the requester can cancel their own booking
    if request.user != booking.requester:
        messages.error(request, 'You can only cancel your own bookings!')
        return redirect('my_bookings')
    
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled.')
        return redirect('my_bookings')
    
    context = {'booking': booking}
    return render(request, 'bookings/booking_confirm_cancel.html', context)


# ============================================================
#  PROFILE VIEWS
# ============================================================

@login_required(login_url='login')
def profile_edit_view(request):
    """
    Edit your profile (bio, avatar, location)
    """
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {'form': form, 'profile': profile}
    return render(request, 'profile/profile_edit.html', context)


def profile_view(request, username):
    """
    View someone else's profile
    
    Shows their skills and ratings
    """
    user = get_object_or_404(User, username=username)
    profile = UserProfile.objects.get_or_create(user=user)[0]
    
    # Get their skills
    skills = user.skills.all()
    
    context = {
        'profile_user': user,
        'profile': profile,
        'skills': skills,
        'rating': profile.average_rating,
    }
    return render(request, 'profile/profile_view.html', context)


# ============================================================
#  SEARCH VIEW
# ============================================================

def search_view(request):
    """
    Search for skills by title, description, or category
    
    This view handles the main search functionality
    """
    skills = Skill.objects.all().order_by('-created_at')
    search_form = SkillSearchForm(request.GET)
    
    query = request.GET.get('query', '')
    category = request.GET.get('category', '')
    
    if query:
        skills = skills.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(owner__username__icontains=query)
        )
    
    if category:
        skills = skills.filter(category=category)
    
    context = {
        'skills': skills,
        'search_form': search_form,
        'query': query,
        'selected_category': category,
        'results_count': skills.count(),
    }
    return render(request, 'search_results.html', context)

