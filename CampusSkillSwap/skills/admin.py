from django.contrib import admin
from .models import Skill, Review, BookingRequest, UserProfile

# ============================================================
#  SKILL ADMIN - Manage skill posts
# ============================================================

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    # What fields show in the list view
    list_display = ('title', 'owner', 'category', 'price', 'availability_status', 'created_at')
    
    # What fields can be clicked to filter
    list_filter = ('category', 'availability_status', 'price', 'created_at')
    
    # Search functionality
    search_fields = ('title', 'description', 'owner__username')
    
    # How fields organized in edit form (read-only = can't change)
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'category')
        }),
        ('Pricing & Contact', {
            'fields': ('price', 'contact_preference', 'contact_info')
        }),
        ('Owner & Status', {
            'fields': ('owner', 'availability_status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Hide by default
        }),
    )
    
    # Don't let admins edit these (set by system)
    readonly_fields = ('created_at', 'updated_at')


# ============================================================
#  REVIEW ADMIN - Manage ratings and reviews
# ============================================================

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('skill', 'reviewer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'skill__category')
    search_fields = ('skill__title', 'reviewer__username', 'comment')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Review Info', {
            'fields': ('skill', 'reviewer', 'rating', 'comment')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


# ============================================================
#  BOOKING REQUEST ADMIN - Manage booking requests
# ============================================================

@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ('skill', 'requester', 'status', 'requested_date', 'created_at')
    list_filter = ('status', 'created_at', 'requested_date')
    search_fields = ('skill__title', 'requester__username', 'message')
    
    fieldsets = (
        ('Booking Info', {
            'fields': ('skill', 'requester', 'status')
        }),
        ('Details', {
            'fields': ('message', 'requested_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


# ============================================================
#  USER PROFILE ADMIN - Manage user profiles
# ============================================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'created_at')
    list_filter = ('created_at', 'location')
    search_fields = ('user__username', 'bio', 'location')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Profile Info', {
            'fields': ('bio', 'avatar', 'location')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

