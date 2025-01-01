# Property Management System

This project is a Django-based Command-Line Interface (CLI) application that integrates the Ollama LLM model to rewrite property information, generate summaries, ratings, and reviews for properties. The application uses Django ORM for database interactions and stores data in a PostgreSQL database. It fetches data from an existing hotels table, rewrites property titles, generates descriptions, and produces summaries, ratings, and reviews using the Ollama model.

## Features

### Core Features
1. **Property Data Fetching:**
   - Fetches property data from the existing `hotels` table in the database, which includes details like title, hotelId, city, location, price, image_path, rating, room_type, latitude, and longitude.

2. **Title and Description Rewriting:**
   - Uses the Ollama model to rewrite property titles and generate detailed descriptions based on the fetched data.

3. **Property Summary Generation:**
   - Automatically generates a concise summary of the property based on the provided details using the selected Ollama model.

4. **Ratings and Reviews Generation:**
   - Generates ratings and reviews for properties using the LLM model and stores them in the database.

5. **Ollama Model Integration:**
   - Integrates with the Ollama model (`llama3.2` model) to generate human-like text based on property data, including title rewriting, descriptions, summaries, and reviews.
 

## Project Structure

```plaintext
Property_Management/
├── Property_Management/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── ollama_app/
│   ├── management/
│   │   ├── commands/
│   │   │   ├── __init__.py
│   │   │   ├── process_properties.py
│   │   ├── __init__.py
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   ├── 0002_propertycontent_propertyid_propertyreview_propertyid_and_more.py
│   │   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── requirements.txt
├── .gitignore
├──  README.md
└── requirements.txt
```



## Project Setup

### Prerequisites

- **Python 3.8+**
- **Django 4.x**
- **PostgreSQL**
- **Ollama**
- **Docker** and **Docker Compose**

### Docker Configuration
This project uses Docker and Docker Compose to run the application with all necessary services, including the PostgreSQL database and Ollama model.
- The `Dockerfile` sets up the application container.
- The `docker-compose.yml` file defines the services required to run the application (Django, PostgreSQL, Ollama etc.).

### Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/Shazid18/Django_LLM.git
   cd Django_LLM
   ```
2. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install project dependencies:
   ```bash
   pip install -r requirements.txt
   ```
 
4. Configure the database in settings.py:
    ```plaintext
    Update DATABASES with your PostgreSQL credentials and enable PostGIS.
    ```
 
### Running the Application
 
1. Docker Set Up:
   ```bash
   cd Inventory_Management
   docker-compose up --build -d
   ```
   
2. Apply migrations:
   ```bash
   docker exec -it django_app python manage.py makemigrations
   docker exec -it django_app python manage.py migrate
   ```

3. Create a superuser:
   ```bash
   docker exec -it django_app python manage.py createsuperuser
   ```

4. Start the server:
   ```bash
   docker exec -it django_app python manage.py runserver
   ```
   
5. Access the application at http://localhost:8000/

## Usage

1. `http://localhost:8000` => Home page

2. `http://localhost:8000/sign-up/` => for Property Owner signup

3. `http://localhost:8000/sign-up/success/` => successful signup. If the admin permite the Active and Staff status of the user then the user can login into the admin pannel.

3. Access the admin panel at `http://localhost:8000/admin/` and log in with your superuser credentials.

## Command-Line Utility

- **Populate initial location data:**
    To populate initial location data, run:
   ```bash
   docker exec -it django_app python manage.py populate_location_data
   ```
   
- **Generate sitemap:**
    To generate the sitemap, open the bash shell:
   ```bash
   docker exec -it django_app bash
   ```
   Then run:
   ```bash
   python manage.py generate_sitemap
   ```
   
- **Update the Property Owners Group:**
    Run the following command to create or update the property owners group:
   ```bash
   docker exec -it django_app python manage.py create_property_owners_group
   ```

## Add accommodation Amenities field

    ```
    [
     "Free Wi-Fi",
     "Air Conditioning",
     "Swimming Pool",
     "Gym Access"
    ]
    ```

## Add Localized Accommodation Aolicy field

- language: en

    ``` 
    {
    "pet_policy" : "Pets are not allowed.",
    "smoking_policy" : "Smoking is prohibited indoors."
    }
    ```
- language: Len

    ``` 
    {
    "pet_policy" : "No se permiten mascotas.",
    "smoking_policy" : "Está prohibido fumar en el interior."
    }
    ```

## CSV Format for Locations

**To import locations via CSV, ensure that the CSV file follows this format:**

   ```bash
   id,title,center,parent,location_type,country_code,state_abbr,city,created_at,updated_at
   BD,Bangladesh,"POINT(90.3563 23.685)",,country,BD,,,,
   BD-CTG,Chittagong,"POINT(91.815536 22.341900)",BD,state,BD,CTG,,,
   BD-CTG-KH,Khulshi,"POINT(91.815536 22.341900)",BD-CTG,city,BD,CTG,"Khulshi",,
   BD-DHA,Dhaka,"POINT(90.4125 23.8103)",BD,state,BD,DHA,,,
   BD-DHA-MI,Mirpur,"POINT(90.4125 23.8103)",BD-DHA,city,BD,DHA,"Mirpur",,
   ```

## Testing
To run unit tests for the project, use:

   ```bash
   docker exec -it django_app python manage.py test
   ```

To see the coverage report, run:

   ```bash
   docker exec -it django_app coverage report
   ```
   
## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Contributing

Feel free to fork the repository and submit pull requests. Please follow the standard GitHub workflow and ensure that any contributions are well-tested.
