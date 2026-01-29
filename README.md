# 3D Print Marketplace

A Django-based multi-vendor marketplace for 3D print files and physical product fulfillment.

## Features
- Multi-role: Visitor, Consumer, Seller, Admin
- Digital file sales and physical product fulfillment
- Stripe payments and payouts
- Moderation, reviews, and legal compliance

## Structure
See the project folders for modular Django apps and configuration.

## Setup
1. Create a virtual environment and install requirements:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and configure environment variables.
3. Run migrations:
   ```bash
   python manage.py migrate
   ```
4. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Docker (optional)
- Use `docker-compose up` to run the project in containers.

---

This project is designed for incremental development and clear separation of concerns.
