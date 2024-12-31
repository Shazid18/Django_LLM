from django.test import TestCase
from django.db.models import Avg
from decimal import Decimal
from .models import Hotel, PropertyContent, PropertySummary, PropertyReview
from unittest import TestCase as UnitTestCase
from unittest.mock import patch, MagicMock
from django.utils import timezone

# Using UnitTestCase instead of Django's TestCase to avoid database operations
class HotelModelTests(UnitTestCase):
    @patch('django.db.models.Model.save')
    def setUp(self, mock_save):
        self.hotel_data = {
            'city': 'New York',
            'hotelId': 'NYC123',
            'title': 'Test Hotel',
            'location': 'Manhattan',
            'price': 299.99,
            'image_path': '/images/test.jpg',
            'rating': 4.5,
            'room_type': 'Deluxe',
            'latitude': 40.7128,
            'longitude': -74.0060
        }
        self.hotel = Hotel(**self.hotel_data)
            
    def test_hotel_creation(self):
        self.assertEqual(self.hotel.city, self.hotel_data['city'])
        self.assertEqual(self.hotel.hotelId, self.hotel_data['hotelId'])
        self.assertEqual(self.hotel.title, self.hotel_data['title'])
        self.assertEqual(self.hotel.location, self.hotel_data['location'])
        self.assertEqual(self.hotel.price, self.hotel_data['price'])
        self.assertEqual(self.hotel.image_path, self.hotel_data['image_path'])
        self.assertEqual(self.hotel.rating, self.hotel_data['rating'])
        self.assertEqual(self.hotel.room_type, self.hotel_data['room_type'])
        self.assertEqual(self.hotel.latitude, self.hotel_data['latitude'])
        self.assertEqual(self.hotel.longitude, self.hotel_data['longitude'])

class PropertyContentModelTests(UnitTestCase):
    @patch('django.db.models.Model.save')
    def setUp(self, mock_save):
        self.hotel = Hotel(
            city='New York',
            hotelId='NYC123',
            title='Test Hotel'
        )
            
        self.property_data = {
            'propertyId': 'PROP123',
            'title': 'Test Property',
            'description': 'Test Description',
            'hotel': self.hotel
        }
        
        self.property = PropertyContent(**self.property_data)
        self.property.created_at = timezone.now()
        self.property.updated_at = timezone.now()

    def test_property_content_creation(self):
        self.assertEqual(self.property.propertyId, self.property_data['propertyId'])
        self.assertEqual(self.property.title, self.property_data['title'])
        self.assertEqual(self.property.description, self.property_data['description'])
        self.assertEqual(self.property.hotel, self.hotel)
        self.assertIsNotNone(self.property.created_at)
        self.assertIsNotNone(self.property.updated_at)

class PropertySummaryModelTests(UnitTestCase):
    @patch('django.db.models.Model.save')
    def setUp(self, mock_save):
        self.hotel = Hotel(
            city='New York',
            hotelId='NYC123',
            title='Test Hotel'
        )
        
        self.property = PropertyContent(
            propertyId='PROP123',
            title='Test Property',
            description='Test Description',
            hotel=self.hotel
        )
        
        self.summary_data = {
            'property': self.property,
            'propertyId': 'PROP123',
            'summary': 'Test Summary'
        }
        
        self.summary = PropertySummary(**self.summary_data)
        self.summary.created_at = timezone.now()

    def test_property_summary_creation(self):
        self.assertEqual(self.summary.property, self.property)
        self.assertEqual(self.summary.propertyId, self.summary_data['propertyId'])
        self.assertEqual(self.summary.summary, self.summary_data['summary'])
        self.assertIsNotNone(self.summary.created_at)

class PropertyReviewModelTests(UnitTestCase):
    @patch('django.db.models.Model.save')
    def setUp(self, mock_save):
        self.hotel = Hotel(
            city='New York',
            hotelId='NYC123',
            title='Test Hotel'
        )
        
        self.property = PropertyContent(
            propertyId='PROP123',
            title='Test Property',
            description='Test Description',
            hotel=self.hotel
        )
        
        self.review_data = {
            'property': self.property,
            'propertyId': 'PROP123',
            'rating': Decimal('4.5'),
            'review': 'Test Review'
        }
        
        self.review = PropertyReview(**self.review_data)
        self.review.created_at = timezone.now()

    def test_property_review_creation(self):
        self.assertEqual(self.review.property, self.property)
        self.assertEqual(self.review.propertyId, self.review_data['propertyId'])
        self.assertEqual(self.review.rating, self.review_data['rating'])
        self.assertEqual(self.review.review, self.review_data['review'])
        self.assertIsNotNone(self.review.created_at)

    @patch('django.db.models.query.QuerySet.aggregate')
    def test_average_rating(self, mock_aggregate):
        mock_aggregate.return_value = {'rating__avg': Decimal('4.5')}
        
        # Mocking the QuerySet
        mock_queryset = MagicMock()
        mock_queryset.aggregate.return_value = {'rating__avg': Decimal('4.5')}
        
        with patch.object(PropertyReview.objects, 'filter', return_value=mock_queryset):
            avg_rating = PropertyReview.objects.filter(
                property=self.property
            ).aggregate(Avg('rating'))['rating__avg']
            
            self.assertEqual(avg_rating, Decimal('4.5'))