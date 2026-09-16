# 🚀 HelpDesk Pro

> A lightweight, full-stack employee support ticketing system designed to mirror real-world enterprise service-management applications. Available in both **Flask + Vanilla JS SPA** and **Streamlit Data App** interfaces.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://app-desk-pro-endcs4mbzgppmzsas52fwl.streamlit.app/)

### 🌐 **Live Interactive Demo:** [app-desk-pro.streamlit.app](https://app-desk-pro-endcs4mbzgppmzsas52fwl.streamlit.app/)

---

## 📖 Overview
HelpDesk Pro is an internal IT/HR support ticketing system built to bridge the gap between basic CRUD apps and enterprise-grade software engineering projects. It allows employees to submit support requests and enables administrators/IT agents to track, manage, filter, and resolve tickets efficiently.

---

## ✨ Features
* **Submit Tickets:** Employees can easily submit new support requests with title, detailed issue description, category, priority level, and requester details.
* **Track & Manage Status:** Filter and manage tickets by lifecycle stage (`Open`, `In Progress`, `Resolved`, `Closed`).
* **Live Search & Filtering:** Instant search across titles, descriptions, and requester names, along with multi-attribute filtering (Status, Priority, Category).
* **Activity & Resolution Notes:** Add internal comments and resolution updates to any ticket for full audit and communication history.
* **Real-Time Metrics Dashboard:** At-a-glance KPI cards displaying total, open, in-progress, and resolved ticket counts.
* **Analytics & Reports:** Interactive category and status distribution charts in the Streamlit interface.
* **Dual Interface Options:**
  - **Flask + Vanilla JS SPA**: Fast RESTful single-page web app.
  - **Streamlit Data App**: Native Python interactive dashboard hostable on Streamlit Community Cloud.

---

## 🌐 Live Demo & Deployment

Try the application live on Streamlit Cloud without local installation:
👉 **[Launch HelpDesk Pro Live Demo](https://app-desk-pro-endcs4mbzgppmzsas52fwl.streamlit.app/)**

---

## 🛠️ Tech Stack

**Frontend & App Frameworks:**
* HTML5 / CSS3 / Vanilla JavaScript (Fetch API)
* Streamlit (`streamlit_app.py`)
* Pandas (Data Analytics)

**Backend:**
* Python 3.x
* Flask (REST API Framework)
* Flask-SQLAlchemy (ORM) & SQLite3

---

## 🚀 Local Setup & Installation

### 1. Installation & Dependencies

```bash
# Clone repository
git clone https://github.com/Divyanjali7467/Help-Desk-Pro.git
cd Help-Desk-Pro

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1   # On Windows
# source .venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Seed sample database
python seed.py
```

### 2. Option A: Run Streamlit Application

```bash
streamlit run streamlit_app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

### 3. Option B: Run Flask RESTful SPA

```bash
python app.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## 📡 REST API Reference (Flask Backend)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/stats` | Retrieve metrics summary counts (Total, Open, In Progress, Resolved, Closed) |
| `GET` | `/api/tickets` | Fetch tickets list with optional query params (`status`, `priority`, `category`, `search`) |
| `GET` | `/api/tickets/<id>` | Fetch details and comments for a single ticket |
| `POST` | `/api/tickets` | Submit a new support ticket |
| `PATCH` | `/api/tickets/<id>` | Update ticket status, priority, or category |
| `DELETE` | `/api/tickets/<id>` | Delete a ticket by ID |
| `POST` | `/api/tickets/<id>/comments` | Add a note or comment to a ticket |

---

## 📁 Directory Structure

```
HelpDesk-Pro/
├── streamlit_app.py       # Streamlit interactive application
├── .streamlit/
│   └── config.toml        # Streamlit theme configuration
├── app.py                 # Flask server & REST API routes
├── models.py              # SQLAlchemy database models (Ticket, Comment)
├── seed.py                # Database initial seed script
├── requirements.txt       # Python dependencies (Flask, Streamlit, Pandas)
├── README.md              # Project documentation
├── static/
│   ├── css/style.css      # Enterprise CSS stylesheet
│   └── js/app.js          # SPA frontend logic & Fetch API integration
└── templates/
    └── index.html         # SPA HTML template
```
