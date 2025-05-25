# SafeLedger

## Group Members
- [Jane Cagorong]
- [Justine Son Camila]
- [Mark Angelo Umacam]


---

## Introduction

SafeLedger Banking App is a web-based banking platform that allows users to register, log in, manage their accounts, and perform transactions such as transfers and deposits. This project was originally developed as a simple demonstration of online banking features and has since been enhanced with robust security measures.

---

## Objectives

- Provide a user-friendly platform for basic banking operations.
- Ensure the confidentiality, integrity, and availability of user data.
- Identify and remediate security vulnerabilities through assessment and best practices.
- Demonstrate secure coding and deployment practices for web applications.

---

## Original Application Features

- User registration and login
- Account dashboard with balance display
- Money transfer between users
- Deposit functionality (admin/manager)
- User management (admin/manager)
- Transaction history
- Password reset via email (simulated)
- Basic input validation

---

## Security Assessment Findings

**Vulnerabilities identified in the original application:**
- Weak or missing input validation on forms
- Insecure session and cookie settings
- Lack of strong password policy enforcement
- Insufficient CSRF protection on some forms
- No custom error pages (information leakage risk)
- Outdated or unpinned dependencies
- No rate limiting on sensitive endpoints
- Potential for SQL injection and XSS due to unsanitized inputs
- Incomplete authorization checks on admin/manager routes
- No enforcement of HTTPS or secure communication

---

## Security Improvements Implemented

- **Input Validation:**  
  Enhanced both client-side and server-side validation for all forms using WTForms and HTML5 attributes.
- **Password Security:**  
  Enforced strong password policies and used bcrypt for secure password hashing.
- **Session Management:**  
  Enabled secure, HTTP-only, and SameSite cookies; implemented session timeouts.
- **CSRF Protection:**  
  Ensured CSRF tokens are present and validated on all forms.
- **Error Handling:**  
  Added custom 404 and 500 error pages to prevent information leakage.
- **Dependency Management:**  
  Pinned all dependencies to specific versions and regularly audited for vulnerabilities.
- **Rate Limiting:**  
  Applied Flask-Limiter to sensitive routes (login, registration, transfers).
- **Output Encoding:**  
  Ensured all user input is properly escaped in templates to prevent XSS.
- **Authorization:**  
  Strengthened role-based access control for admin and manager routes.
- **Secure Communication:**  
  Configured the app to prefer HTTPS and set secure cookie flags.

---

## Penetration Testing Report

**Summary of vulnerabilities identified:**
- Weak password acceptance and lack of complexity checks.
- Session cookies were not marked as Secure or HttpOnly.
- Forms were susceptible to CSRF attacks.
- Some endpoints lacked rate limiting, allowing brute-force attempts.
- Error pages leaked stack traces and sensitive information.

**Exploitation steps:**
- Used OWASP ZAP and Burp Suite to test for XSS, CSRF, and authentication bypass.
- Attempted SQL injection and XSS payloads in form fields.
- Manipulated session cookies to test for session fixation/hijacking.
- Submitted forms without CSRF tokens to test for CSRF vulnerabilities.

**Recommendations:**
- Enforce strong password policies.
- Always use secure, HTTP-only cookies.
- Implement CSRF protection on all forms.
- Add rate limiting to sensitive endpoints.
- Use custom error pages to prevent information leakage.

---

## Remediation Plan

**Steps taken to address identified vulnerabilities:**
1. Implemented strong input validation and password policies.
2. Secured session management and cookies.
3. Added CSRF protection to all forms.
4. Created custom error pages for 404 and 500 errors.
5. Pinned and updated all dependencies; added regular security audits.
6. Applied rate limiting to login, registration, and transfer routes.
7. Reviewed and improved authorization checks for all sensitive routes.
8. Configured the app to use HTTPS and secure cookies.

---

## Technology Stack

- Python 3.x
- Flask 2.x/3.x
- Flask-Login
- Flask-WTF
- Flask-Limiter
- Flask-Bcrypt
- Flask-SQLAlchemy
- PyMySQL
- WTForms
- Bootstrap (for frontend)
- MySQL (database)
- pip-audit (for dependency security)
- OWASP ZAP, Burp Suite, Nikto, Nmap (for security testing)

---

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone https://github.com/jijayne/simple-banking-app-v2.git
   cd secure-simple-banking-app
   ```

2. **Create and activate a virtual environment:**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   - Copy `.env.example` to `.env` and fill in your database and secret key values.

5. **Initialize the database:**
   ```
   python app.py  # The app will auto-create tables and a default admin user if needed
   ```

6. **Run the application:**
   ```
   python app.py
   ```
   - Access the app at [http://localhost:5000](http://localhost:5000)

7. **(Optional) Run security audits:**
   ```
   pip install pip-audit
   pip-audit
   ```
## Cloud Deployment

You can access the live SafeLedger Banking App on our cloud server:

**SafeLegder.pythonanywhere.com**

>
---

**For any questions or issues, please open an issue on the repository.**
