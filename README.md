# GRADRDAR - Graduate Readiness & Career Development Platform

GRADRDAR is a web-based platform designed to help students assess their career readiness, identify skill gaps, receive personalized action plans, and track their progress toward employability goals.

The system provides role-based access for Students and Administrators, allowing efficient management of skills, drives, applications, and readiness reports.

---

## 🚀 Features

### Student Module
- User Registration & Login
- Profile Management
- Readiness Assessment
- Skill Gap Analysis
- Personalized Action Plan Generation
- Drive Application Tracking
- Dashboard with Progress Insights

### Admin Module
- Admin Authentication
- Dashboard Analytics
- Manage Skills
- Manage Placement Drives
- Student Reports
- Career Readiness Monitoring

### Analytics Engine
- Eligibility Checker
- Skill Gap Analyzer
- Readiness Calculator
- Personalized Plan Generator

---

## 🛠️ Tech Stack

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- Flask

### Database
- SQLite

### Other Tools
- Jinja2 Templates
- Bootstrap
- Git & GitHub

---

## 📂 Project Structure

```text
GRADDAR/
│
├── engine/
│   ├── eligibility_checker.py
│   ├── gap_analyzer.py
│   ├── plan_generator.py
│   └── readiness_calculator.py
│
├── models/
│   └── db.py
│
├── routes/
│
├── static/
│   ├── css/
│   ├── images/
│   └── js/
│
├── templates/
│   ├── admin/
│   ├── auth/
│   └── student/
│
├── app.py
├── config.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/your-username/GRADDAR.git
cd GRADDAR
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url
```

### 6. Run Application

```bash
python app.py
```

---

## 🔐 Authentication

The platform supports:

- Student Login
- Student Registration
- Admin Login
- Role-Based Access Control

---

## 📊 Core Functionalities

### Readiness Calculator
Calculates overall student readiness score based on skills, qualifications, and profile data.

### Skill Gap Analysis
Identifies missing skills required for target career opportunities.

### Eligibility Checker
Checks student eligibility for placement drives.

### Action Plan Generator
Generates personalized recommendations for career improvement.

---

## 📸 Screenshots

Add screenshots of:

- Home Page
- Student Dashboard
- Admin Dashboard
- Skill Gap Analysis
- Readiness Report

---

## 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a new branch
3. Commit changes
4. Push changes
5. Create a Pull Request

---

## 📜 License

This project is developed for educational and academic purposes.

© 2026 GRADDAR. All Rights Reserved.
