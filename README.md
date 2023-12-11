# Django E-commerce Application

## Overview

Welcome to the Django E-commerce Application, a semi-functional project designed to showcase expertise in Python and backend APIs. This project is intended for demonstration 
purposes only and is not meant for commercial use. It serves as a comprehensive example of various features and practices within the Django framework.

## Features

* Django Authentication and Authorization
* Django Models for Orders, Products, and Categories Data
* REST APIs for Backend Functionalities
* Handling Multiple Sub-applications in Django
* Ajax for Updating States in Django
* Django Template for UI

## Video of the project
[![Watch the video](https://github.com/lollinng/Django_Eccomerce_project/assets/55660103/55bd62ce-67fd-4043-bd08-07b38276472d)](https://www.youtube.com/watch?v=Fe9ZR5nI-0c&t=26s)

## Getting Started
To explore and run this project locally, follow the steps below:

1. Clone the repository:
  ```bash
  git clone https://github.com/lollinng/Django_Eccomerce_project.git
  ```
2. Install Dependencies using virutal env
  ```bash
  python -m venv env
  env\Scripts\activate.bat
  pip install -r requirements.txt
  ```
3. Intgrate django data models to databasae
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```
4. Run application
  ```bash
  python manage.py runserver.
  ```
5. Add an admin user for managing the site and listing/updating the products
  ```bash
  python manage.py createsuperuser
  ```


## Disclaimer
This project is purely a demonstration of skills and is not intended for production use. Any code snippets or functionalities should be adapted and validated according to best practices before implementation in a live environment.
