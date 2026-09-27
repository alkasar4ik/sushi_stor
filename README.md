# Sakura House

Web application for a Japanese restaurant built with **Python and Flask**.

## Features

* User registration and authentication
* Restaurant menu and products
* Order creation and order history
* Admin panel
* Product management
* User management
* Image upload
* PostgreSQL database

## Technologies

* Python
* Flask
* SQLAlchemy
* Flask-Login
* PostgreSQL
* Pillow
* Jinja2
* HTML / CSS / JavaScript

## Installation

Clone the repository:


git clone https://github.com/USERNAME/sushi_stor.git
cd sushi_stor


Create and activate a virtual environment:


python -m venv venv


Install dependencies:


pip install -r requirements.txt


Create a `.env` file in the project root:


SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://username:password@localhost:5432/sushi


Create a PostgreSQL database named `sushi`.

Run the application:


python app.py


Open in your browser:


http://127.0.0.1:5000


## Project Structure


sushi_stor/
├── static/
├── templates/
├── app.py
├── models.py
├── requirements.txt
├── .env
└── README.md

## Security

* Password hashing
* Protected admin routes
* Environment variables for sensitive data
* User authentication with Flask-Login





