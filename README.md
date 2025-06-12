# Vector Educare (Dynamic Version)

This branch contains the **dynamic web application** for Vector Educare, built with Flask and designed for easy content management via an admin interface.

## About

- **Dynamic Site:** This branch features a dynamic, database-driven version of the Vector Educare website.
- **Admin Panel:** Includes a secure admin dashboard for managing events, teachers, and contact information.
- **Backend:** Powered by Python (Flask) and SQLite for persistent storage.
- **Deployment:** Intended for production deployment using Gunicorn.

## Features

- **Admin Authentication:** Secure login for admin access.
- **Event Management:** Add, edit, and delete events with images and descriptions.
- **Teacher Management:** Manage teacher profiles, including images, subjects, and experience.
- **Contact Info:** Easily update phone numbers and WhatsApp contact.
- **Dynamic Rendering:** All content is rendered dynamically from the database.

## Technologies Used

- **Backend:** Python 3, Flask, SQLite
- **Frontend:** HTML5, CSS3, JavaScript, Jinja2 templates
- **Other Libraries:**
    - [Font Awesome](https://fontawesome.com/) for icons
    - [python-dotenv](https://pypi.org/project/python-dotenv/) for environment variable management
    - [Gunicorn](https://gunicorn.org/) for production WSGI server

## Setup

1. **Clone this branch** and install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2. **Set environment variables** (see `.env.example` or set `APP_SECRET_KEY`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`).
3. **Run the app in production with Gunicorn:**
    ```bash
    gunicorn -c gunicorn_config.py app:app
    ```
4. **Access the admin panel:**  
   Go to `/login` and use your admin credentials.

## Other Versions

- **Static Version:**  
    The `static` branch contains a static version of the site, suitable for GitHub Pages deployment and using FormSubmit for form handling.

