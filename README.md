<div align="center">

<img src="static/Logo/WithoutBg.png" alt="Bookly Logo" width="180"/>

# 🏨 Bookly — Hotel Management System

**Complete Hotel Management, Simplified.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.x-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-blue?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![GitHub](https://img.shields.io/badge/GitHub-Repo-181717?style=for-the-badge&logo=github)](https://github.com/ompandey07/HMS)

</div>

---

## 📖 About Bookly

**Bookly** is a comprehensive web-based Hotel Management System (HMS) built with Django and PostgreSQL. Designed to streamline all hotel operations — from room reservations and guest check-in/check-out to restaurant management, inventory tracking, and detailed MIS reports — everything in one powerful, integrated platform.

> *"A well-managed hotel is one where every guest feels like the most important person in the building."*

---

## ✨ Features

### 🛏️ Room Management
- Room booking, inquiry, and reservation management
- Real-time room availability status
- Customizable room tariff and labeling setup
- Advance booking with deposit collection
- Guest ledger and identity management

### 🔑 Check-In & Check-Out
- Record check-in time and date
- Advance collection with receipt generation
- Room service and laundry billing
- Generate comprehensive room bills
- Extra bed and amenity management
- Check-in / Check-out reports

### 🍽️ Restaurant & Bar Management
- Table and item master management
- Multiple price menus and complementary items
- KOT (Kitchen Order Ticket) management with pending order tracking
- Cashier-wise cash management
- Service tax and VAT calculation
- Transfer bills to room accounts
- Separate bar and restaurant management
- Daily collection flash reports

### 📦 Stores & Purchases
- Complete item and inventory management
- Purchase order maintenance
- Inter-location stock transfers
- Location-wise stock reports
- Detailed inventory reports

### 📊 MIS Reports
| Category | Reports |
|---|---|
| **Room Reports** | Booked room details, Reservation report, Room register, Bill settlement, Empty rooms |
| **Guest Reports** | Current guest list, Present & past guests, Billed & settled guests, Guest ledger |
| **Financial Reports** | Advance booking register, Daily collection, Room bill settlement, Maintenance expenses |
| **Operations Reports** | Room shifting, Cancellation report, Rooms under maintenance, Security reports |

---

## 🗂️ Project Structure

```
HMS/
├── accounts/          # User authentication & management
├── billing/           # Billing and invoicing
├── bookings/          # Room bookings and reservations
├── core/              # Core app settings & base views
├── Frontend/          # Frontend assets and templates
├── guests/            # Guest management
├── HMS/               # Main Django project settings
├── media/             # Uploaded media files
├── referrals/         # Referral management
├── reports/           # MIS reports module
├── rooms/             # Room management
├── staff/             # Staff management
├── static/            # Static files (CSS, JS, images)
├── .env               # Environment variables (not committed)
├── .gitignore
└── manage.py
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/ompandey07/HMS.git
cd HMS
```

### 2. Create & Activate Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root of the project:

```dotenv
SECRET_KEY=django-insecure-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database
DB_NAME=HMS
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

> ⚠️ **Never commit your `.env` file.** It is already listed in `.gitignore`.

### 5. Create PostgreSQL Database

```sql
CREATE DATABASE HMS;
CREATE USER your_db_user WITH PASSWORD 'your_db_password';
GRANT ALL PRIVILEGES ON DATABASE HMS TO your_db_user;
```

### 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser

```bash
python manage.py createsuperuser
```

### 8. Collect Static Files

```bash
python manage.py collectstatic
```

### 9. Start the Development Server

```bash
python manage.py runserver
```

Open your browser and navigate to: **http://127.0.0.1:8000**

---

## 🔐 Admin Panel

Access the Django admin panel at:

```
http://127.0.0.1:8000/admin
```

Log in with the superuser credentials you created.

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django (Python) |
| Database | PostgreSQL |
| Frontend | HTML, CSS, JavaScript |
| Icons | Remix Icons, Lucide Icons |
| Fonts | Inter, Poppins, Kaushan Script |

---

## 📬 Contact & Repository

- 🔗 **GitHub:** [https://github.com/ompandey07/HMS](https://github.com/ompandey07/HMS)

---

<div align="center">

Made with ❤️ by **Om Pandey**

*Bookly — Product Which Never Demands Service*

</div>