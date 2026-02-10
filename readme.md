# 🥐 Bakery Management System – Web Application

A full-stack **Bakery Management Web Application** designed to manage products, orders, billing, and daily operations efficiently.  
This project demonstrates real-world workflow implementation with a clean UI and fast performance.

---

##  Features
- User authentication (Login / Logout)
- Product management (Add / Update / Delete)
- Order & billing workflow
- Automatic total calculation
- Dashboard-style interface
- Fast and responsive UI

---

## Tech Stack
- **Backend:** Django
- **Database:** PostgreSQL
- **Frontend:** HTML, CSS, JavaScript
- **Version Control:** Git & GitHub

---

## Demo
🎥 A short demo video is available on my LinkedIn profile showing the full workflow of the application.

---

## ⚙️ Installation & Setup

1. Clone the repository:
#### git clone https://github.com/srikanthbanothu26/Bakery-website.git
#### cd bakery-management-system

2. Create and activate virtual environment:

#### python -m venv venv
#### source venv/bin/activate   
#### venv\Scripts\activate



3. Install dependencies:

pip install -r requirements.txt


4. Configure database:

Update database settings in settings.py

5. Run migrations:

python manage.py migrate


6. Create superuser:

python manage.py createsuperuser


7. Run the server:

python manage.py runserver