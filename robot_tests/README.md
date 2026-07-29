# 🤖 KPIT Auth Platform - Robot Framework Tests
Automated test suite for the KPIT Auth Platform using Robot Framework.

## 📋 Prerequisites
- Python 3.11+
- Flask backend running on `http://localhost:5000`
- Chrome browser (for UI tests, coming soon)

## 🚀 Installation
```bash
# Create virtual environment
python -m venv venv
# Activate it (Windows)
venv\Scripts\activate
# Install dependencies
pip install -r requirements.txt
🧪 Running Tests
Bash
# Run all tests
robot -d results suites/
# Run specific test suite
robot -d results suites/01_health_tests.robot
# Run tests with tags
robot -d results --include smoke suites/

📊 View Reports
After running tests, open:

results/report.html - Executive summary
results/log.html - Detailed logs

📁 Project Structure
text
robot_tests/
├── suites/          # Test suites
├── resources/       # Reusable keywords
├── data/            # Test data (CSV, JSON)
└── results/         # Generated reports (git-ignored)

👤 Author
Khammar Mohamed Dhia - KPIT Summer Internship 2026