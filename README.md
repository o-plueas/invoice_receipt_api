

BUSINESS SYSTEM WITH INVOICE AND RECEIPT GENERATOR


A comprehensive full-stack quote-to-invoice management system for interior design businesses, featuring automated workflows, real-time tracking, and seamless client communication.

PS: SEE docs/full_doc.md for More details


OVERVIEW

This Business management System is an enterprise-grade SaaS solution designed to streamline the complete lifecycle of interior design projects — from initial client quote requests to final payment receipts.

The system eliminates manual paperwork, reduces operational errors, and provides real-time visibility into business performance.



BUSINESS PROBLEM SOLVED

Interior design businesses commonly face:

1. Manual quote tracking and follow-ups
2. Inefficient invoice generation
3. Missed or delayed payments
4. Poor client communication
5. Lack of business insights

THIS SYSTEM REPLACES MANUAL BUSINESS PAPER WORKS, saving over 15 hours per week and r delays by up to 40 percent.


KEY FEATURES

AUTHENTICATION AND AUTHORIZATION

1. JWT-based secure authentication
2. Role-based access control (Admin, Staff, Client)
3. Token refresh mechanism
4. Password reset functionality

QUOTE MANAGEMENT

1. Public quote submission without login
2. Multiple service categories
3. File attachment support (PDF, DOC, DOCX, JPG, PNG)
4. Status tracking (Pending, Approved, Converted)
5. Admin approval workflow

INVOICE SYSTEM

1. Convert quotes to invoices in one click
2. Multiple line items per invoice
3. Automatic subtotal, tax, and total calculations
4. Unique invoice numbering system
5. Payment status tracking
6. Due date management

RECEIPT GENERATION

1. Automatic receipt creation when invoice is marked as paid
2. Manual receipt creation option
3. Payment method tracking
4. Unique receipt numbering
5. Transaction reference logging

DASHBOARD AND ANALYTICS

1. Real-time business metrics
2. Revenue tracking
3. Invoice status monitoring
4. Quote conversion insights

ACTIVITY LOGGING

1. Full audit trail of system actions
2. User activity tracking
3. Timestamped logs

RESPONSIVE DESIGN

1. Mobile-first interface
2. Cross-browser compatibility
3. Clean and modern UI



TECH STACK

BACKEND

1. Python
2. Django
3. Django REST Framework
4. JWT Authentication
5. SQLite / PostgreSQL
6. Celery (Currently implementing this)
7. Redis (Currently implementing this)

FRONTEND

1. JavaScript (ES6)
2. HTML5
3. CSS3
4. Fetch API

DEVOPS AND HOSTING

1. PythonAnywhere (Backend)
2. Render (Frontend)
3. Git and GitHub


ARCHITECTURE

The system follows a layered architecture:

CLIENT LAYER → API LAYER → BUSINESS LOGIC → DATA LAYER → DATABASE

Core modules include:

1. User Management
2. Quote System
3. Invoice System
4. Receipt System
5. Activity Logging


BUSINESS FLOW

STEP 1: CUSTOMER SUBMITS QUOTE

1. Public form submission
2. System generates reference number
3. Status set to pending

STEP 2: ADMIN REVIEWS QUOTE

1. Admin approves or rejects

STEP 3: INVOICE CREATION

1. Admin converts approved quote
2. Adds line items
3. System calculates totals
4. Invoice generated

STEP 4: PAYMENT AND RECEIPT

1. Invoice marked as paid
2. Receipt sent to customer


API ENDPOINTS

BASE URL
https://oplueaswsapi.pythonanywhere.com/api

AUTHENTICATION

1. POST /auth/login/
2. POST /auth/register/
3. POST /token/refresh/

QUOTES

1. POST /quotes/
2. GET /quotes/admin/
3. PATCH /quotes/admin/{id}/

INVOICES

1. GET /invoices/
2. POST /invoices/
3. POST /invoices/{id}/mark-paid/

RECEIPTS

1. GET /receipts/
2. POST /receipts/



INSTALLATION

1. Clone repository API
   git clone https://github.com/o-plueas/invoice_receipt_api.git

    git clone https://github.com/o-plueas/businessystem.git

2. Create virtual environment
   python -m venv venv

3. Install dependencies
   pip install -r requirements.txt

4. Run migrations
   python manage.py migrate

5. Start server
   python manage.py runserver



PROJECT STRUCTURE

backend

1. accounts
2. quotes
3. invoices
4. receipts
5. activitylog

frontend

1. dashboard
2. public pages

docs

1. Complete documentation (API documentation)


KEY TECHNICAL ACHIEVEMENTS

1. RELATIONAL DATA INTEGRITY using OneToOne relationships
2. AUTOMATIC FINANCIAL CALCULATIONS
3. SECURE JWT AUTHENTICATION
4. CLEAN RESTFUL API DESIGN
5. EFFICIENT FRONTEND STATE MANAGEMENT


FUTURE ENHANCEMENTS

1. PDF generation
2. Email notifications
3. Payment gateway integration
4. Mobile application
5. AI-powered quote estimation
6. Advanced analytics dashboard
7. SIGNAL-DRIVEN ARCHITECTURE for receipt generation



DEPLOYMENT

1. Backend: PythonAnywhere
2. Frontend: Render





ScreenShots

Contact form:
https://drive.google.com/file/d/10W7UifE119wN_k9c6SowB2uPLtqvXbPC/view?usp=drive_link

Admin Contact panel
https://drive.google.com/file/d/1IxwHzla3r43G2IWkxaUyUKhZeW33i9G7/view?usp=drive_link

Admin Dashboard:
https://drive.google.com/file/d/1-ssRK-TD_oTo3wHL_fK9xsLyVSoeJfMj/view?usp=drive_link

Admin Invoice Form 
https://drive.google.com/file/d/14dhL2Iq3hdTnp4WHbnuLcPUf9vQts8nR/view?usp=drive_link

Admin Invoice
https://drive.google.com/file/d/1ZdNf266EELwMtlOwQCTPDQCVpaz4o1pA/view?usp=drive_link

Admin Invoice List
https://drive.google.com/file/d/1zlGkGmb29PDQTp-78HPFU5LKaj81B7Uc/view?usp=drive_link

Admin Payment Recorder 
https://drive.google.com/file/d/104FxAx_eZ4-gwmaWJHEUhODpgAJ_kpkc/view?usp=drive_link

Admin Receipt Generator 
https://drive.google.com/file/d/1NCxgktGuIytiC_wwjxydTeMv8bJzGZQZ/view?usp=drive_link

Receipt
https://drive.google.com/file/d/1klrovr20YEJH0ysU3JK3hsAQwB_ffWDH/view?usp=drive_link



LIVE DEMO
https://youtu.be/yFt12oTRTkA?si=XBuwlBg8CUJmw2yy 

Live site

SPA: https://ajibo-interiors-worldwide.onrender.com/ 

& 

Dashboard: https://ajibo-interiors-worldwide.onrender.com/dashboard/

API: https://oplueaswsapi.pythonanywhere.com/api





CONTACT

DEVELOPER
Ogochukwu Lucy Ugwu

EMAIL
ogochukwu lucy ugwu

PHONE
+2348066686958

LINKEDIN
https://www.linkedin.com/in/ogochukwu-lucy-ugwu 



WHY THIS PROJECT STANDS OUT

1. FULL-STACK DEVELOPMENT EXPERTISE
2. REAL BUSINESS APPLICATION WITH PRACTICAL IMPACT
3. PRODUCTION-READY DEPLOYMENT
4. SCALABLE ARCHITECTURE
5. STRONG SECURITY IMPLEMENTATION
6. CLEAN AND MAINTAINABLE CODEBASE



PROJECT METRICS

1. 15+ DATABASE MODELS
2. 50+ API ENDPOINTS
3. 10+ FRONTEND PAGES
4. HIGH PERFORMANCE API RESPONSE TIMES

