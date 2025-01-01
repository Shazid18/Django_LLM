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
                json={"model": self.model, "prompt": prompt, "stream": False},
                stream=False
            )
            response.raise_for_status()
            
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

    def generate_property_description_and_modify_title(self, hotel: Hotel) -> Dict[str, str]:
        prompt = f"""Modify the title and generate a description for this hotel property. Respond EXACTLY in this format:
            TITLE: [modify the title with a catchy, SEO-friendly title under 100 characters]
            DESCRIPTION: [write a detailed description highlighting the location, amenities, and unique features]

            Hotel Information:
            - Title: {hotel.title}
            - Location: {hotel.location}, {hotel.city}
            - Price: ${hotel.price}
            - Room Type: {hotel.room_type}
            - Rating: {hotel.rating}

            Focus only on providing the TITLE and DESCRIPTION under the respective markers. DO NOT include any other text or information."""
        
        try:
            response = self.ollama.generate(prompt)
            
            # Split response using exact markers
            title = ""
            description = ""
            
            if "TITLE:" in response and "DESCRIPTION:" in response:
                # Find the indices of the markers
                title_start = response.find("TITLE:") + 6
                desc_start = response.find("DESCRIPTION:") + 12
                desc_end = len(response)
                
                # Extract title (everything between TITLE: and DESCRIPTION:)
                title = response[title_start:response.find("DESCRIPTION:")].strip()
                
                # Extract description (everything after DESCRIPTION:)
                description = response[desc_start:desc_end].strip()
            else:
                raise ValueError("Response format incorrect: Missing TITLE: or DESCRIPTION: markers")
            
            return {
                'title': title[:255],  # Ensure title fits in database field
                'description': description
            }
        except Exception as e:
            logger.error(f"Error generating property description: {str(e)}")
            raise

    def generate_summary(self, hotel: Hotel, property_content: PropertyContent) -> str:
        prompt = f"""Create a concise one-paragraph summary of the following property. Respond EXACTLY in this format:
            SUMMARY: [write a summary under 500 characters, no other text or information]

            Hotel Information:
            - Title: {hotel.title}
            - Location: {hotel.location}, {hotel.city}
            - Price: ${hotel.price}
            - Room Type: {hotel.room_type}
            - Rating: {hotel.rating}
            - Description: {property_content.description}

            Focus only on the key selling points of the property and make sure the response is just the summary under 500 characters. DO NOT include any other text, just the summary under the "SUMMARY:" marker."""
        
        try:
            response = self.ollama.generate(prompt)
            
            summary = ""
            
            if "SUMMARY:" in response:
                # Find the index of the SUMMARY: marker
                summary_start = response.find("SUMMARY:") + 8
                summary = response[summary_start:].strip()
            else:
                raise ValueError("Response format incorrect: Missing SUMMARY: marker")
            
            # Ensure summary doesn't exceed 500 characters
            return summary[:500]
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise

    def generate_review(self, hotel: Hotel, property_content: PropertyContent) -> Dict[str, Any]:
        prompt = f"""Generate a realistic guest review based on this property. Respond EXACTLY in this format:
            RATING: [number between 1.0-5.0]
            REVIEW: [write a detailed guest review]

            Hotel Information:
            - Title: {hotel.title}
            - Location: {hotel.location}, {hotel.city}
            - Price: ${hotel.price}
            - Room Type: {hotel.room_type}
            - Rating: {hotel.rating}
            - Description: {property_content.description}"""
        
        try:
            response = self.ollama.generate(prompt)
            
            rating = 4.0  # Default rating
            review = ""
            
            if "RATING:" in response and "REVIEW:" in response:
                # Find the indices of the markers
                rating_start = response.find("RATING:") + 7
                review_start = response.find("REVIEW:") + 7
                
                # Extract rating
                rating_str = response[rating_start:response.find("REVIEW:")].strip()
                try:
                    rating = float(rating_str)
                except ValueError:
                    rating = 4.0  # Default rating if parsing fails
                
                # Extract review
                review = response[review_start:].strip()
            else:
                raise ValueError("Response format incorrect: Missing RATING: or REVIEW: markers")
            
            return {
                'rating': min(max(rating, 1.0), 5.0),  # Ensure rating is between 1.0 and 5.0
                'review': review
            }
        except Exception as e:
            logger.error(f"Error generating review: {str(e)}")
            raise

    @transaction.atomic
    def handle(self, *args, **options):
        hotels = Hotel.objects.all().order_by('-id')[:2]  # Limit to 2 properties for testing
        self.stdout.write(f"Processing {len(hotels)} properties...")
        
        success_count = 0
        error_count = 0

        for hotel in hotels:
            try:
                # Generate and save property content
                content_data = self.generate_property_description_and_modify_title(hotel)
                property_content = PropertyContent.objects.create(
                    hotel=hotel,
                    title=content_data['title'],
                    description=content_data['description'],
                    propertyId=hotel.hotelId
                    
                )

                # Generate and save summary
                summary = self.generate_summary(hotel, property_content)
                PropertySummary.objects.create(
                    property=property_content,
                    summary=summary,
                    propertyId=hotel.hotelId
                )

                # Generate and save review
                review_data = self.generate_review(hotel, property_content)
                PropertyReview.objects.create(
                    property=property_content,
                    rating=review_data['rating'],
                    review=review_data['review'],
                    propertyId=hotel.hotelId
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