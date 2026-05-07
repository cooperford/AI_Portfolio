"""
Django Forms for Campus SkillSwap
==================================
Forms handle:
- User registration and authentication
- Creating and editing skills
- Leaving reviews
- Booking skill sessions
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Skill, Review, BookingRequest, UserProfile


# ============================================================
#  AUTHENTICATION FORMS
# ============================================================

class RegisterForm(UserCreationForm):
    """
    Registration form - lets new users create accounts
    
    Built on Django's UserCreationForm which handles:
    - Valid username
    - Email address
    - Strong password checking
    - Password confirmation
    """
    
    email = forms.EmailField(
        required=True,
        help_text="We'll use this for account recovery"
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        help_text="Optional - your first name"
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        help_text="Optional - your last name"
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add bootstrap styling to all fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
    
    def clean_email(self):
        """Make sure email isn't already registered"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered!")
        return email


class LoginForm(forms.Form):
    """
    Simple login form - just username and password
    (Django provides a built-in LoginView, but we can customize here if needed)
    """
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


# ============================================================
#  USER PROFILE FORMS
# ============================================================

class UserProfileForm(forms.ModelForm):
    """
    Form for editing user profile (bio, avatar, location)
    """
    
    class Meta:
        model = UserProfile
        fields = ('bio', 'avatar', 'location')
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell other users about yourself...'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Building A, East Campus'
            }),
        }


# ============================================================
#  SKILL FORMS
# ============================================================

class SkillForm(forms.ModelForm):
    """
    Form for creating or editing a skill posting
    
    Users fill this out when they want to offer a new skill
    """
    
    class Meta:
        model = Skill
        # Don't include 'owner' - we'll set it to the logged-in user in the view
        fields = ('title', 'description', 'category', 'price', 
                  'contact_preference', 'contact_info', 'availability_status')
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., "Learn Python Programming"'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'What will you teach? What should students bring? Etc.'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Price per session (0 for free)',
                'step': '0.01',
                'min': '0'
            }),
            'contact_preference': forms.Select(attrs={
                'class': 'form-control'
            }),
            'contact_info': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your email, phone, etc.'
            }),
            'availability_status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def clean_price(self):
        """Make sure price isn't negative"""
        price = self.cleaned_data.get('price')
        if price and price < 0:
            raise forms.ValidationError("Price can't be negative!")
        return price


class SkillSearchForm(forms.Form):
    """
    Simple search form for finding skills
    """
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search skills...'
        })
    )
    category = forms.ChoiceField(
        required=False,
        choices=[('', 'All Categories')] + list(Skill.CATEGORY_CHOICES),
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )


# ============================================================
#  REVIEW FORMS
# ============================================================

class ReviewForm(forms.ModelForm):
    """
    Form for leaving a review/rating on a skill
    
    After using someone's skill, they fill this out
    """
    
    class Meta:
        model = Review
        # Don't include 'skill', 'reviewer', 'created_at' - set in view
        fields = ('rating', 'comment')
        
        widgets = {
            'rating': forms.RadioSelect(
                choices=[(i, f'{i} ⭐') for i in range(1, 6)],
                attrs={'class': 'form-check-input'}
            ),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience with other students...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create radio buttons for rating
        self.fields['rating'] = forms.ChoiceField(
            choices=[(i, f'{i} ⭐') for i in range(1, 6)],
            widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
            help_text="How would you rate this skill?"
        )


# ============================================================
#  BOOKING REQUEST FORMS
# ============================================================

class BookingRequestForm(forms.ModelForm):
    """
    Form for requesting to book a skill session
    
    When a user wants to learn a skill, they fill this out
    """
    
    class Meta:
        model = BookingRequest
        # Don't include 'skill', 'requester', 'status', timestamps
        fields = ('requested_date', 'message')
        
        widgets = {
            'requested_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'placeholder': 'When would you like to meet?'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell the skill owner when you\'re available and any other details...'
            }),
        }


class BookingRequestReplyForm(forms.ModelForm):
    """
    Form for skill owner to approve or reject a booking request
    """
    
    class Meta:
        model = BookingRequest
        fields = ('status',)
        
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show relevant status choices for replies
        self.fields['status'].choices = [
            ('pending', 'Still Pending'),
            ('approved', 'Approve Request'),
            ('rejected', 'Reject Request'),
        ]
