from django.contrib import admin
from .models import Hotel, PropertyContent, PropertySummary, PropertyReview

# Register Hotel model


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('hotelId', 'title', 'city')
    search_fields = ('hotelId', 'title', 'city')
    list_filter = ('city', 'rating')
    ordering = ('city', 'title')

# Register PropertyContent model


@admin.register(PropertyContent)
class PropertyContentAdmin(admin.ModelAdmin):
    list_display = ('propertyId', 'title', 'hotel', 'created_at')
    # hotel__title is used to search by related hotel title
    search_fields = ('propertyId', 'title', 'hotel__title')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

# Register PropertySummary model


@admin.register(PropertySummary)
class PropertySummaryAdmin(admin.ModelAdmin):
    list_display = ('propertyId', 'property', 'created_at')
    search_fields = ('propertyId', 'property__title',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)

# Register PropertyReview model


@admin.register(PropertyReview)
class PropertyReviewAdmin(admin.ModelAdmin):
    list_display = ('propertyId', 'property', 'rating', 'created_at')
    search_fields = ('propertyId', 'property__title',)
    list_filter = ('rating', 'created_at')
    ordering = ('-created_at',)
