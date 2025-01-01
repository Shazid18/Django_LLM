# import json
# import unittest
# from unittest.mock import patch, MagicMock, call

# import requests
# from ollama_app.management.commands.process_properties import Command, OllamaClient

# class TestOllamaClient(unittest.TestCase):
#     def setUp(self):
#         self.client = OllamaClient()

#     @patch('requests.post')
#     def test_generate_success(self, mock_post):
#         mock_response = MagicMock()
#         mock_response.json.return_value = {'response': 'test response'}
#         mock_post.return_value = mock_response
        
#         result = self.client.generate("test prompt")
#         self.assertEqual(result, 'test response')
        
#         mock_post.assert_called_once_with(
#             "http://ollama:11434/api/generate",
#             json={"model": "llama3.2", "prompt": "test prompt", "stream": False},
#             stream=False
#         )

#     @patch('requests.post')
#     def test_generate_request_exception(self, mock_post):
#         mock_post.side_effect = requests.exceptions.RequestException("API error")
#         with self.assertRaises(requests.exceptions.RequestException):
#             self.client.generate("test prompt")

#     @patch('requests.post')
#     def test_generate_json_decode_error(self, mock_post):
#         mock_response = MagicMock()
#         mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
#         mock_post.return_value = mock_response
        
#         with self.assertRaises(json.JSONDecodeError):
#             self.client.generate("test prompt")

# class TestProcessProperties(unittest.TestCase):
#     def setUp(self):
#         self.command = Command()
#         self.hotel_mock = MagicMock()
#         self.hotel_mock.hotelId = 1
#         self.hotel_mock.title = "Sample Hotel"
#         self.hotel_mock.location = "Beachside"
#         self.hotel_mock.city = "Oceanview"
#         self.hotel_mock.price = 200
#         self.hotel_mock.room_type = "Suite"
#         self.hotel_mock.rating = 4.5

#     def test_generate_property_description_success(self):
#         with patch.object(OllamaClient, 'generate') as mock_generate:
#             mock_generate.return_value = """TITLE: Luxurious Beachside Escape
#             DESCRIPTION: Experience unparalleled comfort with ocean views."""
            
#             result = self.command.generate_property_description_and_modify_title(self.hotel_mock)
            
#             self.assertEqual(result['title'], "Luxurious Beachside Escape")
#             self.assertEqual(result['description'], "Experience unparalleled comfort with ocean views.")

#     def test_generate_property_description_invalid_format(self):
#         with patch.object(OllamaClient, 'generate') as mock_generate:
#             mock_generate.return_value = "Invalid format response"
            
#             with self.assertRaises(ValueError):
#                 self.command.generate_property_description_and_modify_title(self.hotel_mock)

#     def test_generate_summary_success(self):
#         property_content = MagicMock()
#         property_content.description = "Test description"
        
#         with patch.object(OllamaClient, 'generate') as mock_generate:
#             mock_generate.return_value = "SUMMARY: A wonderful beachfront property"
            
#             result = self.command.generate_summary(self.hotel_mock, property_content)
#             self.assertEqual(result, "A wonderful beachfront property")

#     def test_generate_summary_invalid_format(self):
#         property_content = MagicMock()
#         property_content.description = "Test description"
        
#         with patch.object(OllamaClient, 'generate') as mock_generate:
#             mock_generate.return_value = "Invalid format response"
            
#             with self.assertRaises(ValueError):
#                 self.command.generate_summary(self.hotel_mock, property_content)

#     def test_generate_review_success(self):
#         property_content = MagicMock()
#         property_content.description = "Test description"
        
#         with patch.object(OllamaClient, 'generate') as mock_generate:
#             mock_generate.return_value = """RATING: 4.8
#             REVIEW: Excellent stay with great amenities"""
            
#             result = self.command.generate_review(self.hotel_mock, property_content)
#             self.assertEqual(result['rating'], 4.8)
#             self.assertEqual(result['review'], "Excellent stay with great amenities")

#     def test_generate_review_invalid_rating(self):
#         property_content = MagicMock()
#         property_content.description = "Test description"
        
#         with patch.object(OllamaClient, 'generate') as mock_generate:
#             mock_generate.return_value = """RATING: invalid
#             REVIEW: Excellent stay"""
            
#             result = self.command.generate_review(self.hotel_mock, property_content)
#             self.assertEqual(result['rating'], 4.0)  # Should use default rating
#             self.assertEqual(result['review'], "Excellent stay")

#     def test_generate_review_out_of_range_rating(self):
#         property_content = MagicMock()
#         property_content.description = "Test description"
        
#         with patch.object(OllamaClient, 'generate') as mock_generate:
#             mock_generate.return_value = """RATING: 6.0
#             REVIEW: Excellent stay"""
            
#             result = self.command.generate_review(self.hotel_mock, property_content)
#             self.assertEqual(result['rating'], 5.0)  # Should be capped at 5.0

#     @patch('ollama_app.management.commands.process_properties.Hotel.objects')
#     @patch('ollama_app.management.commands.process_properties.PropertyContent.objects.create')
#     @patch('ollama_app.management.commands.process_properties.PropertySummary.objects.create')
#     @patch('ollama_app.management.commands.process_properties.PropertyReview.objects.create')
#     @patch.object(OllamaClient, 'generate')
#     def test_handle_success(self, mock_generate, mock_create_review, mock_create_summary, 
#                           mock_create_content, mock_hotel_objects):
#         # Your existing handle success test...
#         mock_queryset = MagicMock()
#         mock_queryset.order_by.return_value = [self.hotel_mock]
#         mock_hotel_objects.all.return_value = mock_queryset

#         mock_generate.side_effect = [
#             "TITLE: Luxurious Beachside Escape\nDESCRIPTION: Experience unparalleled comfort.",
#             "SUMMARY: A luxurious beachfront hotel offering stunning views.",
#             "RATING: 4.7\nREVIEW: The perfect getaway."
#         ]

#         self.command.handle()

#         self.assertEqual(mock_generate.call_count, 3)
#         mock_create_content.assert_called_once()
#         mock_create_summary.assert_called_once()
#         mock_create_review.assert_called_once()

#     @patch('ollama_app.management.commands.process_properties.Hotel.objects')
#     @patch('ollama_app.management.commands.process_properties.PropertyContent.objects.create')
#     @patch.object(OllamaClient, 'generate')
#     def test_handle_with_errors(self, mock_generate, mock_create_content, mock_hotel_objects):
#         mock_queryset = MagicMock()
#         mock_queryset.order_by.return_value = [self.hotel_mock]
#         mock_hotel_objects.all.return_value = mock_queryset

#         # Simulate an error during content generation
#         mock_generate.side_effect = Exception("Test error")

#         self.command.handle()  # Should handle the error gracefully

#         mock_generate.assert_called_once()
#         mock_create_content.assert_not_called()

#     def test_handle_empty_queryset(self):
#         with patch('ollama_app.management.commands.process_properties.Hotel.objects') as mock_hotel_objects:
#             mock_queryset = MagicMock()
#             mock_queryset.order_by.return_value = []
#             mock_hotel_objects.all.return_value = mock_queryset

#             self.command.handle()  # Should handle empty queryset gracefully

# if __name__ == '__main__':
#     unittest.main()