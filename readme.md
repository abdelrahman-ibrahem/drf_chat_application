# DRF chat application 

This backend repository powers our chat application, providing a robust foundation for real-time communication between users. It leverages the following technologies:

- Django: A high-level Python web framework known for its flexibility, scalability, and reliability.

- Django Rest Framework (DRF): A powerful toolkit for building Web APIs in Django, facilitating smooth client-server interactions through RESTful APIs.

- Django Channels: Extends Django to handle WebSockets, enabling instant messaging and real-time updates.

# Key Features
Real-Time Communication: Utilizes Django Channels for seamless, instant messaging between users.

RESTful APIs: Developed with DRF to ensure efficient client-server interactions.

Scalable Architecture: Designed to handle increasing user loads without compromising performance.

Security Measures: Implements industry best practices to safeguard user data and maintain a secure environment.

# Getting Started
Clone the repository.

git clone git@github.com:abdelrahman-ibrahem/drf_chat_application.git
cd drf_chat_application

# Set up a virtual environment and install dependencies.
- python -m venv venv

- for Linux => source venv/bin/activate
- for Windows => source venv/Scripts/activate
- pip install -r requirements.txt

# Apply database migrations.
- python manage.py makemigrations
- python manage.py migrate

# Start the development server.
- python manage.py runserver
