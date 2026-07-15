# 🔐 KPIT Auth Platform

> **AI-Enhanced Authentication Platform with Intelligent Automated Testing**  
> Summer Internship Project 2026 at KPIT Technologies

[![Python](https://img.shields.io/badge/Python-3.11-blue)]()
[![Angular](https://img.shields.io/badge/Angular-17-red)]()
[![Flask](https://img.shields.io/badge/Flask-3.0-green)]()
[![Robot Framework](https://img.shields.io/badge/Robot%20Framework-7.0-yellow)]()

---

## 📋 Table of Contents

- [About](#-about)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Roadmap](#-roadmap)
- [Getting Started](#-getting-started)
- [Author](#-author)

---

## 🎯 About

This project is developed as part of the **Summer Internship 2026** at **KPIT Technologies**.

The goal is to design, develop and test a **web-based authentication platform** enriched with:

- 🔒 **Enterprise-grade security** (JWT, bcrypt, RBAC, 2FA)
- 🤖 **Artificial Intelligence** (ML Anomaly Detection, LLM Test Generation)
- 🧪 **Comprehensive test automation** using Robot Framework
- 🚀 **DevOps practices** (Docker, CI/CD, Monitoring)

---

## 🏗️ Architecture
┌─────────────────────────────────────────────┐
│ FRONTEND (Angular + Material) │
├─────────────────────────────────────────────┤
│ BACKEND (Flask REST API) │
├─────────────────────────────────────────────┤
│ AI LAYER (ML + LLM) │
├─────────────────────────────────────────────┤
│ DATABASE (SQLite / MySQL) │
├─────────────────────────────────────────────┤
│ TESTING (Robot Framework + Selenium) │
└─────────────────────────────────────────────┘

text


---

## 🛠️ Technology Stack

### Frontend
- **Angular 17+** with TypeScript
- **Angular Material** (UI components)
- **Bootstrap 5** (grid & utilities)
- **Chart.js** (data visualization)

### Backend
- **Python 3.11+**
- **Flask 3.0+** (REST API)
- **SQLAlchemy** (ORM)
- **PyJWT** (authentication)
- **bcrypt** (password hashing)

### AI / ML
- **Scikit-learn** (Anomaly Detection)
- **Ollama + Llama 3.2** (LLM Test Generation)

### Testing
- **Robot Framework 7+**
- **SeleniumLibrary**

### DevOps
- **Docker + Docker Compose**
- **GitHub Actions** (CI/CD)

---

## 📁 Project Structure
kpit-auth-platform/
├── backend/ # Flask REST API
├── frontend/ # Angular application
├── robot_tests/ # Automated tests
├── docs/ # Documentation
└── README.md

text


---

## 🗺️ Roadmap

The project follows a **layered strategy** ensuring a deliverable at every stage:

### ✅ Layer 0 - CORE (Weeks 1-3)
- [x] Project setup
- [ ] Flask REST API
- [ ] Angular frontend
- [ ] SQLite database
- [ ] Robot Framework test suite

### 🔒 Layer 1 - Security+ (Weeks 3-4)
- [ ] JWT authentication
- [ ] Password hashing (bcrypt)
- [ ] Rate limiting
- [ ] RBAC (Role-Based Access Control)
- [ ] Audit logs

### 🤖 Layer 2 - Basic AI (Weeks 5-6)
- [ ] ML Anomaly Detection
- [ ] Analytics dashboard

### 🚀 Layer 3 - Advanced AI (Post-Internship)
- [ ] LLM Test Generation
- [ ] Self-Healing Tests
- [ ] 2FA + OAuth2

### 📦 Layer 4 - DevOps (Post-Internship)
- [ ] Docker containerization
- [ ] CI/CD Pipeline
- [ ] Cloud deployment
- [ ] Monitoring

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Angular CLI 17+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/meddeiaa/kpit-auth-platform.git
cd kpit-auth-platform

# Setup backend (instructions coming soon)
cd backend
# ...

# Setup frontend (instructions coming soon)
cd ../frontend
# ...
👤 Author
Khammar Mohamed Dhia
2nd Year Engineering Student in Computer Science
Higher Institute of Computer Science and Multimedia of Sfax (ISIMS)

GitHub: @meddeiaa
Internship at: KPIT Technologies - Sfax
Supervisor: Smaoui Souhail
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
Special thanks to my supervisor Mr. Smaoui Souhail and the KPIT Technologies team for the opportunity and guidance.