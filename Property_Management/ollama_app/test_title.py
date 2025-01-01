import unittest
from unittest.mock import patch, MagicMock
from ollama_app.management.commands.process_properties import Command, OllamaClient

from ollama_app.models import Hotel, PropertyContent, PropertySummary, PropertyReview

class TestProcessProperties(unittest.TestCase):

    @patch('ollama_app.management.commands.process_properties.Hotel.objects')
    @patch('ollama_app.management.commands.process_properties.PropertyContent.objects.create')
    @patch('ollama_app.management.commands.process_properties.PropertySummary.objects.create')
    @patch('ollama_app.management.commands.process_properties.PropertyReview.objects.create')
    @patch.object(OllamaClient, 'generate')
    def test_handle(self, mock_generate, mock_create_review, mock_create_summary, mock_create_content, mock_hotel_objects):
        # Mock hotel data
        hotel_mock = MagicMock()
        hotel_mock.hotelId = 1
        hotel_mock.title = "Sample Hotel"
        hotel_mock.location = "Beachside"
        hotel_mock.city = "Oceanview"
        hotel_mock.price = 200
        hotel_mock.room_type = "Suite"
        hotel_mock.rating = 4.5
        
        # Mock queryset behavior
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = [hotel_mock]
        mock_queryset.count.return_value = 1
        mock_hotel_objects.all.return_value = mock_queryset

        # Mock responses from OllamaClient
        mock_generate.side_effect = [
            "TITLE: Luxurious Beachside Escape\nDESCRIPTION: Experience unparalleled comfort with ocean views and top-notch amenities.",
            "SUMMARY: A luxurious beachfront hotel offering stunning views, elegant rooms, and exceptional service.",
            "RATING: 4.7\nREVIEW: The perfect getaway with amazing staff and world-class facilities."
        ]

        # Instantiate command and call handle
        command = Command()
        command.handle()

        # Assertions
        mock_create_content.assert_called_once_with(
            hotel=hotel_mock,
            title="Luxurious Beachside Escape",
            description="Experience unparalleled comfort with ocean views and top-notch amenities.",
            propertyId=1
        )
        mock_create_summary.assert_called_once_with(
            property=mock_create_content.return_value,
            summary="A luxurious beachfront hotel offering stunning views, elegant rooms, and exceptional service.",
            propertyId=1
        )
        mock_create_review.assert_called_once_with(
            property=mock_create_content.return_value,
            rating=4.7,
            review="The perfect getaway with amazing staff and world-class facilities.",
            propertyId=1
        )
        mock_generate.assert_any_call(
        """Modify the title and generate a description for this hotel property. Respond EXACTLY in this format:
            TITLE: [modify the title with a catchy, SEO-friendly title under 100 characters]
            DESCRIPTION: [write a detailed description highlighting the location, amenities, and unique features]

            Hotel Information:
            - Title: Sample Hotel
            - Location: Beachside, Oceanview
            - Price: $200
            - Room Type: Suite
            - Rating: 4.5"""
    )


if __name__ == "__main__":
    unittest.main()
