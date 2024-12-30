# management/commands/process_properties.py
from django.core.management.base import BaseCommand
from django.db import transaction
import requests
import json
import logging
from typing import Dict, Any

from ...models import Hotel, PropertyContent, PropertySummary, PropertyReview

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, base_url: str = "http://ollama:11434"):
        self.base_url = base_url
        self.model = "llama3.2"

    def generate(self, prompt: str) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},  # Set stream to False
                stream=False  # Don't stream the response
            )
            response.raise_for_status()  # Raise an exception for bad status codes
            
            # Parse the JSON response
            response_data = response.json()
            return response_data.get('response', '')
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to Ollama API: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON response: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in generate(): {str(e)}")
            raise

class Command(BaseCommand):
    help = 'Process properties using Ollama LLM'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ollama = OllamaClient()

    def generate_property_description(self, hotel: Hotel) -> Dict[str, str]:
        prompt = f"""
        Based on the following hotel information, generate two separate sections:
        1. A catchy, SEO-friendly title (keep it under 100 characters)
        2. A detailed description highlighting the location, amenities, and unique features

        Hotel Information:
        - Location: {hotel.location}, {hotel.city}
        - Price: ${hotel.price}
        - Room Type: {hotel.room_type}
        - Rating: {hotel.rating}

        Format your response as:
        TITLE: [Your title here]
        DESCRIPTION: [Your description here]
        """
        
        try:
            response = self.ollama.generate(prompt)
            
            # Parse response using the TITLE and DESCRIPTION markers
            title_start = response.find("TITLE:") + 6
            desc_start = response.find("DESCRIPTION:") + 12
            
            if title_start < 6 or desc_start < 12:  # If markers not found
                # Fallback parsing - split by double newline
                parts = response.split('\n\n', 1)
                title = parts[0].strip()
                description = parts[1].strip() if len(parts) > 1 else response.strip()
            else:
                # Use markers to extract content
                title_end = response.find("DESCRIPTION:") if "DESCRIPTION:" in response else len(response)
                title = response[title_start:title_end].strip()
                description = response[desc_start:].strip()
            
            return {
                'title': title[:255],  # Ensure title fits in database field
                'description': description
            }
        except Exception as e:
            logger.error(f"Error generating property description: {str(e)}")
            raise

    def generate_summary(self, property_content: PropertyContent) -> str:
        prompt = f"""
        Create a concise one-paragraph summary of the following property:

        Title: {property_content.title}
        Description: {property_content.description}

        Keep the summary under 500 characters and focus on the key selling points.
        """
        
        try:
            return self.ollama.generate(prompt)
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise

    def generate_review(self, property_content: PropertyContent) -> Dict[str, Any]:
        prompt = f"""
        Generate a realistic guest review based on this property:

        Title: {property_content.title}
        Description: {property_content.description}

        Format your response as:
        RATING: [number between 1.0-5.0]
        REVIEW: [detailed guest review]
        """
        
        try:
            response = self.ollama.generate(prompt)
            
            # Parse response using the RATING and REVIEW markers
            rating_start = response.find("RATING:") + 7
            review_start = response.find("REVIEW:") + 7
            
            if rating_start < 7 or review_start < 7:  # If markers not found
                # Fallback parsing
                parts = response.split('\n', 1)
                try:
                    rating = float(parts[0].strip())
                except ValueError:
                    rating = 4.0  # Default rating if parsing fails
                review = parts[1].strip() if len(parts) > 1 else response.strip()
            else:
                # Use markers to extract content
                rating_end = response.find("REVIEW:")
                rating_str = response[rating_start:rating_end].strip()
                try:
                    rating = float(rating_str)
                except ValueError:
                    rating = 4.0  # Default rating if parsing fails
                review = response[review_start:].strip()
            
            return {
                'rating': min(max(rating, 1.0), 5.0),  # Ensure rating is between 1.0 and 5.0
                'review': review
            }
        except Exception as e:
            logger.error(f"Error generating review: {str(e)}")
            raise

    @transaction.atomic
    def handle(self, *args, **options):
        hotels = Hotel.objects.all()
        self.stdout.write(f"Processing {hotels.count()} properties...")
        
        success_count = 0
        error_count = 0

        for hotel in hotels:
            try:
                # Generate and save property content
                content_data = self.generate_property_description(hotel)
                property_content = PropertyContent.objects.create(
                    hotel=hotel,
                    title=content_data['title'],
                    description=content_data['description']
                )

                # Generate and save summary
                summary = self.generate_summary(property_content)
                PropertySummary.objects.create(
                    property=property_content,
                    summary=summary
                )

                # Generate and save review
                review_data = self.generate_review(property_content)
                PropertyReview.objects.create(
                    property=property_content,
                    rating=review_data['rating'],
                    review=review_data['review']
                )

                success_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f"Successfully processed property {hotel.hotelId}"
                ))

            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(
                    f"Error processing property {hotel.hotelId}: {str(e)}"
                ))
                logger.error(f"Error processing property {hotel.hotelId}", exc_info=True)

        # Print summary
        self.stdout.write("\nProcessing completed:")
        self.stdout.write(f"Successfully processed: {success_count} properties")
        self.stdout.write(f"Failed to process: {error_count} properties")