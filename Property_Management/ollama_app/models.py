# models.py
from django.db import models

class Hotel(models.Model):
    city = models.CharField(max_length=255)
    hotelId = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    price = models.FloatField(null=True, blank=True)
    image_path = models.CharField(max_length=255)
    rating = models.FloatField(null=True, blank=True)
    room_type = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'hotels'
        managed = False  # Since this table already exists, we don't want Django to manage it

class PropertyContent(models.Model):
    propertyId = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='content')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'property_content'

class PropertySummary(models.Model):
    property = models.ForeignKey(PropertyContent, on_delete=models.CASCADE, related_name='summaries')
    propertyId = models.CharField(max_length=255, null=True, blank=True)
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'property_summaries'

class PropertyReview(models.Model):
    property = models.ForeignKey(PropertyContent, on_delete=models.CASCADE, related_name='reviews')
    propertyId = models.CharField(max_length=255, null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'property_reviews'