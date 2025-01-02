# Django CLI Application Using Ollama Model

## Table of Contents
  
  1. [Project Overview](#project-overview)
  2. [Features](#features)
  3. [Project Structure](#project-structure)
  4. [Getting Started](#getting-started)
     - [Prerequisites](#prerequisites)
     - [Docker Configuration](#docker-configuration)
     - [Installation Steps](#installation-steps)
     - [Load Ollama model](#load-ollama-model)
     - [Run Application](#running-the-application)
     - [Docker Configuration](#docker-configuration)
  5. [Usage](#usage)
  2. [Testing](#testing)
  3. [Contributing](#contributing)


## Project Overview

This project is a Django-based Command-Line Interface (CLI) application that integrates the Ollama LLM model to rewrite property information, generate summaries, ratings, and reviews for properties. The application uses Django ORM for database interactions and stores data in a PostgreSQL database. It interacts with a PostgreSQL database to fetch property data, then utilizes Ollama to generate human-like text, including property titles, descriptions, summaries, ratings, and reviews.

## Features

1. **Property Data Fetching:**
   - Fetches property details (title, location, price, image, etc.) from the `hotels` table in the database.

2. **Title and Description Rewriting:**
   - Uses Ollama model to rewrite titles and generate detailed descriptions.

3. **Property Summary Generation:**
   - Automatically generates concise summaries based on property details.

4. **Ratings and Reviews Generation:**
   - Generates ratings and reviews using Ollama and stores them in the database.

5. **Ollama Model Integration:**
   - Integrates the `llama3.2` model for content generation.
 

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



## Getting Started

### Prerequisites

- **Python 3.8+**
- **Django 4.x**
- **PostgreSQL**
- **Ollama**
- **Docker** and **Docker Compose**

### Docker Configuration
The project uses Docker and Docker Compose to run the application and services (PostgreSQL, Ollama). The `Dockerfile` defines the application container, and `docker-compose.yml` manages services.

### Installation Steps

1. Clone the Scrapy Repository:
     ```bash
     git clone https://github.com/Shazid18/Scrapy_LLM.git
     ```
     ```bash
     cd Scrapy_LLM
     ```
  
2. Set up a virtual environment:
     ```bash
     python3 -m venv venv
     ```
     
3. Activate the virtual environment:
     ```bash
     source venv/bin/activate   # On Windows: venv\Scripts\activate
     ```
  
4. Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
     
5. Run Docker:
     ```bash
     cd Scrapy_V2
     ```
     ```bash
     docker-compose up --build
     ```
     Now it will start Scrape Data from https://uk.trip.com/hotels/?locale=en-GB&curr=GBP and store those data into Postgres Database.

     Keep the Scrapy project's docker up and then follow the next instructions.

6. Clone the Django LLM Repository in another mother folder:
   ```bash
   git clone https://github.com/Shazid18/Django_LLM.git
   ```
   ```bash
   cd Django_LLM
   ```
7. Set up a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   ```

8. Activate the virtual environment:
     ```bash
     source venv/bin/activate   # On Windows: venv\Scripts\activate
     ```

9. Install project dependencies:
   ```bash
   pip install -r requirements.txt
   ```
 
10. Configure PostgreSQL in  `settings.py` :
    ```plaintext
    Update the `DATABASES` section with the credentials for the Scrapy project's PostgreSQL database.
    ```
 
11. Start Docker :
      ```bash
      cd Property_Management
      ```
      ```bash
      docker-compose up --build -d
      ```
 
### Load Ollama model
 
1. Start Ollama container :
   ```bash
   docker exec -it ollama /bin/bash
   ```

2. Pull and load the model (`llama3.2`) :
   ```bash
   ollama pull llama3.2
   ```

3. Verify the model is loaded :
   ```bash
   ollama list
   ```

4. Exit Ollama container :
   ```bash
   exit
   ```

### Running the Application

#### 1. Restart the Docker services:
   ```bash
   docker-compose down
   ```
   ```bash
   docker-compose up --build -d
   ```

   This will apply migrations and create the required tables (`PropertyContent`, `PropertySummary`, `PropertyReview`).

#### 2. Access services :

   - **Django Web App**: http://localhost:8000

   - **pgAdmin**: http://localhost:5050 (Username: `admin@admin.com` , Password: `admin`).


## Usage

### 1. Generate Property Data

Run the following command to rewrite property titles, descriptions, generate summaries, ratings, and reviews using the Ollama model:

```bash
docker exec -it django_container python manage.py process_properties
```

This will generate AI generated re-written property titles and descriptions and generate property summaries, ratings and reviews for `5 properties`.

To modify the number of properties processed, update the `ollama_app/management/commands/process_properties.py` file (line 168). Example:

- `hotels = Hotel.objects.all().order_by('-id')[:10]` for 10 properties.
- `hotels = Hotel.objects.all().order_by('-id')` for all property.


### 2. Analyze the Data

- **Using Django Admin**:
  - To access Django admin create a superadmin by execute these commands :
  ```bash
  docker exec -it django_container python manage.py createsuperuser
  ```
  - Register these credentials:
    - `Username`: `admin`
    - `Email Address`: `admin@admin.com`
    - `Password`: `admin132456`
    - Bypass password validation and create user anyway? [y/N]: y
  - Go to http://localhost:8000/admin/
  - Enter these credentials and log in:
    - `Username`: `admin`
    - `Password`: `admin132456`
  - Click on **PropertyContent** to view the updated title and description of properties.
  - Click on **PropertySummary** to view the updated summary of properties.
  - Click on **PropertyReview** to view the updated ratings and reviews of properties.

- **Using PgAdmin**:
  - Go to http://localhost:5050/
  - Enter these credentials and press the `Login` button:
    - `Email Address / Username`: `admin@admin.com`
    - `Password`: `admin`
  - Right click on `Servers` and then `Register` > `Server`
  - In `General` tab, enter `Name`: `PostgreSQL`
  - In `Connection` tab, enter these details and click `Save`
    - `Host name/address`: `db`
    - `Port`: `5432`
    - `Username`: `user`
    - `Password`: `password`
  - Then go to ***Servers > PostgreSQL > Databases > scrapy_db > Schemas > public > Tables***
  - To view the AI generated names and description of hotels, right click on the **PropertyContent** table and click on `View/Edit Data` > `All Rows`
  - To view the AI generated summary of hotels, right click on the **PropertySummary** table and click on `View/Edit Data` > `All Rows`
  - To view the AI generated ratings and reviews of hotels, right click on the **PropertyReview** table and click on `View/Edit Data` > `All Rows`


## Testing
Run tests using coverage :

   ```bash
   docker exec -it django_container coverage run manage.py test
   ```

View the coverage report :

   ```bash
   docker exec -it django_container coverage report
   ```


## Contributing

Feel free to fork the repository and submit pull requests. Please follow the standard GitHub workflow and ensure that any contributions are well-tested.
