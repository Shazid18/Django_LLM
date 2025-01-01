from django.test import TestCase
from django.db.models import Avg
from decimal import Decimal
from .models import Hotel, PropertyContent, PropertySummary, PropertyReview
from unittest import TestCase as UnitTestCase
from unittest.mock import patch, MagicMock
from django.utils import timezone

import json
import unittest
from unittest.mock import patch, MagicMock, call

import requests
from ollama_app.management.commands.process_properties import Command, OllamaClient

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
        self.assertEqual(self.property.propertyId,
                         self.property_data['propertyId'])
        self.assertEqual(self.property.title, self.property_data['title'])
        self.assertEqual(self.property.description,
                         self.property_data['description'])
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
        self.assertEqual(self.summary.propertyId,
                         self.summary_data['propertyId'])
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
        self.assertEqual(self.review.propertyId,
                         self.review_data['propertyId'])
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


############################################################################################################


# testing the management command
class TestOllamaClient(unittest.TestCase):
    def setUp(self):
        self.client = OllamaClient()

    @patch('requests.post')
    def test_generate_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {'response': 'test response'}
        mock_post.return_value = mock_response

        result = self.client.generate("test prompt")
        self.assertEqual(result, 'test response')

        mock_post.assert_called_once_with(
            "http://ollama:11434/api/generate",
            json={"model": "llama3.2", "prompt": "test prompt", "stream": False},
            stream=False
        )

    @patch('requests.post')
    def test_generate_request_exception(self, mock_post):
        mock_post.side_effect = requests.exceptions.RequestException(
            "API error")
        with self.assertRaises(requests.exceptions.RequestException):
            self.client.generate("test prompt")

    @patch('requests.post')
    def test_generate_json_decode_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.side_effect = json.JSONDecodeError(
            "Invalid JSON", "", 0)
        mock_post.return_value = mock_response

        with self.assertRaises(json.JSONDecodeError):
            self.client.generate("test prompt")


class TestProcessProperties(unittest.TestCase):
    def setUp(self):
        self.command = Command()
        self.hotel_mock = MagicMock()
        self.hotel_mock.hotelId = 1
        self.hotel_mock.title = "Sample Hotel"
        self.hotel_mock.location = "Beachside"
        self.hotel_mock.city = "Oceanview"
        self.hotel_mock.price = 200
        self.hotel_mock.room_type = "Suite"
        self.hotel_mock.rating = 4.5

    def test_generate_property_description_success(self):
        with patch.object(OllamaClient, 'generate') as mock_generate:
            mock_generate.return_value = """TITLE: Luxurious Beachside Escape
            DESCRIPTION: Experience unparalleled comfort with ocean views."""

            result = self.command.generate_property_description_and_modify_title(
                self.hotel_mock)

            self.assertEqual(result['title'], "Luxurious Beachside Escape")
            self.assertEqual(
                result['description'], "Experience unparalleled comfort with ocean views.")

    def test_generate_property_description_invalid_format(self):
        with patch.object(OllamaClient, 'generate') as mock_generate:
            mock_generate.return_value = "Invalid format response"

            with self.assertRaises(ValueError):
                self.command.generate_property_description_and_modify_title(
                    self.hotel_mock)

    def test_generate_summary_success(self):
        property_content = MagicMock()
        property_content.description = "Test description"

        with patch.object(OllamaClient, 'generate') as mock_generate:
            mock_generate.return_value = "SUMMARY: A wonderful beachfront property"

            result = self.command.generate_summary(
                self.hotel_mock, property_content)
            self.assertEqual(result, "A wonderful beachfront property")

    def test_generate_summary_invalid_format(self):
        property_content = MagicMock()
        property_content.description = "Test description"

        with patch.object(OllamaClient, 'generate') as mock_generate:
            mock_generate.return_value = "Invalid format response"

            with self.assertRaises(ValueError):
                self.command.generate_summary(
                    self.hotel_mock, property_content)

    def test_generate_review_success(self):
        property_content = MagicMock()
        property_content.description = "Test description"

        with patch.object(OllamaClient, 'generate') as mock_generate:
            mock_generate.return_value = """RATING: 4.8
            REVIEW: Excellent stay with great amenities"""

            result = self.command.generate_review(
                self.hotel_mock, property_content)
            self.assertEqual(result['rating'], 4.8)
            self.assertEqual(result['review'],
                             "Excellent stay with great amenities")

    def test_generate_review_invalid_rating(self):
        property_content = MagicMock()
        property_content.description = "Test description"

        with patch.object(OllamaClient, 'generate') as mock_generate:
            mock_generate.return_value = """RATING: invalid
            REVIEW: Excellent stay"""

            result = self.command.generate_review(
                self.hotel_mock, property_content)
            # Should use default rating
            self.assertEqual(result['rating'], 4.0)
            self.assertEqual(result['review'], "Excellent stay")

    def test_generate_review_out_of_range_rating(self):
        property_content = MagicMock()
        property_content.description = "Test description"

        with patch.object(OllamaClient, 'generate') as mock_generate:
            mock_generate.return_value = """RATING: 6.0
            REVIEW: Excellent stay"""

            result = self.command.generate_review(
                self.hotel_mock, property_content)
            self.assertEqual(result['rating'], 5.0)  # Should be capped at 5.0

    @patch('ollama_app.management.commands.process_properties.Hotel.objects')
    @patch('ollama_app.management.commands.process_properties.PropertyContent.objects.create')
    @patch('ollama_app.management.commands.process_properties.PropertySummary.objects.create')
    @patch('ollama_app.management.commands.process_properties.PropertyReview.objects.create')
    @patch.object(OllamaClient, 'generate')
    def test_handle_success(self, mock_generate, mock_create_review, mock_create_summary,
                            mock_create_content, mock_hotel_objects):
        # Your existing handle success test...
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = [self.hotel_mock]
        mock_hotel_objects.all.return_value = mock_queryset

        mock_generate.side_effect = [
            "TITLE: Luxurious Beachside Escape\nDESCRIPTION: Experience unparalleled comfort.",
            "SUMMARY: A luxurious beachfront hotel offering stunning views.",
            "RATING: 4.7\nREVIEW: The perfect getaway."
        ]

        self.command.handle()

        self.assertEqual(mock_generate.call_count, 3)
        mock_create_content.assert_called_once()
        mock_create_summary.assert_called_once()
        mock_create_review.assert_called_once()

    @patch('ollama_app.management.commands.process_properties.Hotel.objects')
    @patch('ollama_app.management.commands.process_properties.PropertyContent.objects.create')
    @patch.object(OllamaClient, 'generate')
    def test_handle_with_errors(self, mock_generate, mock_create_content, mock_hotel_objects):
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = [self.hotel_mock]
        mock_hotel_objects.all.return_value = mock_queryset

        # Simulate an error during content generation
        mock_generate.side_effect = Exception("Test error")

        self.command.handle()  # Should handle the error gracefully

        mock_generate.assert_called_once()
        mock_create_content.assert_not_called()

    def test_handle_empty_queryset(self):
        with patch('ollama_app.management.commands.process_properties.Hotel.objects') as mock_hotel_objects:
            mock_queryset = MagicMock()
            mock_queryset.order_by.return_value = []
            mock_hotel_objects.all.return_value = mock_queryset

            self.command.handle()  # Should handle empty queryset gracefully


if __name__ == '__main__':
    unittest.main()
