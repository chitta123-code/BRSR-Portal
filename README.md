# BRSR Portal – AI-Powered ESG Reporting Platform

An AI-assisted Business Responsibility and Sustainability Reporting (BRSR) and Environmental, Social, and Governance (ESG) management platform built using Python and Django.

The platform is designed to simplify ESG data collection, validation, evidence verification, review, consolidation, and BRSR report generation.

## Project Overview

Organizations need to collect and manage ESG information from different subsidiaries and business units. Managing this information manually can be time-consuming and error-prone.

**BRSR Portal** aims to digitize this process through a centralized web-based platform with structured workflows, data validation, anomaly detection, and evidence management.

## Key Features

- **Organization Management:** Manage groups, subsidiaries, and business units.
- **ESG Data Management:** Collect and manage Environmental, Social, and Governance data.
- **Excel Data Import:** Upload ESG data through Excel files.
- **Smart Data Validation:** Validate submitted ESG information.
- **Anomaly Detection:** Identify potentially unusual or inconsistent ESG data.
- **Evidence Management:** Upload and verify supporting documents.
- **Evidence Matching:** Match supporting evidence with relevant ESG records.
- **Review Workflow:** Support manager and reviewer activities.
- **Data Consolidation:** Consolidate ESG information across organizational units.
- **BRSR Reporting:** Support BRSR report preparation and PDF generation.

## Technology Stack

| Category | Technologies |
|---|---|
| Backend | Python, Django |
| Frontend | HTML, CSS, Bootstrap |
| Database | MySQL |
| Data Processing | Python, Excel processing |
| Machine Learning / Analytics | Anomaly detection and validation modules |
| Version Control | Git, GitHub |

## Application Workflow

1. Organization and business-unit setup.
2. ESG data entry or Excel upload.
3. Data validation and anomaly checking.
4. Supporting evidence upload and verification.
5. Manager and reviewer assessment.
6. ESG data consolidation.
7. BRSR report preparation and generation.

## Project Structure

```text
BRSR-Portal/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── esg_data/
│   ├── models.py
│   ├── views.py
│   ├── validators.py
│   └── services/
│
├── evidence/
├── indicators/
├── ingestion/
├── organization/
├── reporting/
├── reports/
├── support/
├── validation/
├── workflow/
│
├── templates/
├── manage.py
├── requirements.txt
└── README.md
```

*Note: The structure above highlights the main project modules.*

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/chitta123-code/BRSR-Portal.git
cd BRSR-Portal
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the database

Create a MySQL database:

```sql
CREATE DATABASE esg_brsr_db;
```

Configure your database connection and Django secret key using local environment variables. Do not commit passwords, secret keys, or other credentials to GitHub.

### 5. Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create an administrator account

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

Open the application:

```text
http://127.0.0.1:8000/
```

Admin panel:

```text
http://127.0.0.1:8000/admin/
```

## Screenshots

Add screenshots of your actual application here.

Suggested screenshots:

- Main dashboard
- ESG data upload page
- Data validation dashboard
- Anomaly detection dashboard
- Evidence verification page
- Manager review dashboard
- BRSR report page

Example:

```markdown
![Dashboard](screenshots/dashboard.png)
```

## Future Enhancements

- Advanced machine-learning-based ESG anomaly detection.
- Automated ESG evidence extraction using OCR.
- Improved BRSR reporting and analytics.
- Interactive ESG performance dashboards.
- Cloud deployment and role-based access improvements.

## Project Purpose

This project explores how web technologies, data processing, and AI-assisted validation can help organizations manage ESG information and streamline BRSR reporting workflows.

## Disclaimer

This is an educational and development project. Its outputs should be reviewed and validated before being used for official regulatory reporting.

## Repository

GitHub: https://github.com/chitta123-code/BRSR-Portal