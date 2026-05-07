"""
Skills App Models
=================
This file defines the database structure for:
- Skill (the skill/service posting)
- Review (ratings and comments on skills)
- BookingRequest (when someone requests to book a skill session)
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Skill(models.Model):
    """
    Represents a skill or service that a user offers to others
    
    Examples:
    - Title: "Learn Python Programming"
    - Category: "Technology"
    - Price: 20.00 (per hour) or 0 (free)
    - Status: "available" (currently offering this skill)
    """
    
    # Category choices - what type of skill this is
    CATEGORY_CHOICES = [
        ('technology', 'Technology & Programming'),
        ('language', 'Languages'),
        ('arts', 'Arts & Music'),
        ('sports', 'Sports & Fitness'),
        ('academics', 'Academic Help'),
        ('business', 'Business & Entrepreneurship'),
        ('lifestyle', 'Lifestyle & Wellness'),
        ('other', 'Other'),
    ]
    
    # Availability status choices
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('busy', 'Temporarily Unavailable'),
        ('inactive', 'Inactive'),
    ]
    
    # Contact preference choices
    CONTACT_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('in_person', 'In Person'),
        ('online', 'Online Meeting'),
    ]
    
    # Basic information
    title = models.CharField(
        max_length=100,
        help_text="e.g., 'Learn Guitar Basics', 'Python Tutoring'"
    )
    description = models.TextField(
        help_text="Describe what you'll teach, what students will learn"
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other'
    )
    
    # Pricing information
    price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Set to 0 for free. Price per hour/session."
    )
    
    # Owner & Contact
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # If user deleted, delete their skills too
        related_name='skills'  # Access via user.skills.all()
    )
    contact_preference = models.CharField(
        max_length=20,
        choices=CONTACT_CHOICES,
        default='email'
    )
    contact_info = models.CharField(
        max_length=255,
        blank=True,
        help_text="Your email, phone, or other contact info"
    )
    
    # Status & Timestamps
    availability_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available'
    )
    created_at = models.DateTimeField(auto_now_add=True)  # Set once, never changes
    updated_at = models.DateTimeField(auto_now=True)     # Updates every save
    
    # For ordering & display
    class Meta:
        ordering = ['-created_at']  # Show newest first
        verbose_name_plural = "Skills"
    
    def __str__(self):
        """What shows up when you print a Skill object"""
        return f"{self.title} by {self.owner.username}"
    
    @property
    def average_rating(self):
        """Calculate average rating from reviews"""
        reviews = self.reviews.all()
        if not reviews:
            return 0
        total = sum(review.rating for review in reviews)
        return round(total / len(reviews), 1)


class Review(models.Model):
    """
    A review/rating for a skill
    
    Example:
    - Reviewer: "john_doe" (the person who TOOK the skill)
    - Skill: "Learn Python Programming" (the skill being reviewed)
    - Rating: 5 (out of 5)
    - Comment: "Amazing teacher! Learned so much!"
    """
    
    # Link to the skill being reviewed
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='reviews'  # Access via skill.reviews.all()
    )
    
    # Who wrote the review
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews_written'  # Access via user.reviews_written.all()
    )
    
    # Rating (1-5 stars)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rate from 1 (poor) to 5 (excellent)"
    )
    
    # Written comment
    comment = models.TextField(
        blank=True,
        help_text="Optional - share your experience"
    )
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        # Prevent duplicate reviews from same person for same skill
        unique_together = ('skill', 'reviewer')
    
    def __str__(self):
        return f"Review of '{self.skill.title}' by {self.reviewer.username} - {self.rating}⭐"


class BookingRequest(models.Model):
    """
    When a user requests to book a skill session
    
    Flow:
    1. User A sees Skill by User B
    2. User A sends BookingRequest (message: "I'm free Tuesday at 3pm")
    3. User B can approve/reject
    4. If approved, they arrange meeting
    """
    
    # Status options
    STATUS_CHOICES = [
        ('pending', 'Pending (Awaiting Response)'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # The skill being booked
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='booking_requests'
    )
    
    # Who is requesting
    requester = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='booking_requests_made'
    )
    
    # Request details
    message = models.TextField(
        help_text="Tell the skill owner when you're available and any other details"
    )
    requested_date = models.DateTimeField(
        help_text="When you'd like to do this skill session"
    )
    
    # Status & Management
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Request to book '{self.skill.title}' by {self.requester.username}"


class UserProfile(models.Model):
    """
    Extended user profile - stores extra info about users beyond Django's default User model
    
    Django's User model has: username, email, first_name, last_name
    This adds: bio, avatar, location, rating
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    bio = models.TextField(
        blank=True,
        max_length=500,
        help_text="Tell other users about yourself"
    )
    
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text="Profile picture"
    )
    
    location = models.CharField(
        max_length=100,
        blank=True,
        help_text="Your city or campus location"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def average_rating(self):
        """Calculate average rating as a skill owner"""
        skills = self.user.skills.all()
        total_rating = 0
        total_reviews = 0
        
        for skill in skills:
            reviews = skill.reviews.all()
            if reviews:
                total_rating += sum(review.rating for review in reviews)
                total_reviews += len(reviews)
        
        if total_reviews == 0:
            return 0
        return round(total_rating / total_reviews, 1)

