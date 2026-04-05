# SmartAgri Robot — Control Center

A full-stack IoT-based smart agriculture robot control system built with Flask,
ESP32, and AI. Enables real-time robot control, sensor monitoring, automated
farming operations, and AI-powered crop assistance.

## Features

- Real-time robot control via WiFi (forward, back, left, right, stop)
- Live ESP32-CAM feed with capture and recording
- Soil moisture, temperature, and humidity sensor dashboard
- AI Farming Assistant using TF-IDF crop recommendation
- Smart auto-irrigation based on soil data + weather forecast
- Weather forecast (Bangalore) with 6-day outlook
- Inventory and maintenance tracking
- Team Hub messaging
- Light/Dark mode

## Tech Stack

**Hardware:** ESP32, ESP32-CAM, DHT11/DHT22, Capacitive Soil Sensor, Relay Module

**Backend:** Python 3.10, Flask, MySQL

**Frontend:** HTML5, Bootstrap 5, Chart.js, Leaflet.js

**AI/ML:** TF-IDF Vectorizer, Cosine Similarity (scikit-learn)

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/vikram-p23/smartagri-robot.git
cd smartagri-robot
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

### 5. Set up the database
- Install XAMPP and start MySQL
- Create a database named `Robot_db`
- Import the schema: see `database/schema.sql`

### 6. Run the app
```bash
python app.py
```

Visit `http://localhost:5000`

## ESP32 API Endpoints

Update the IP in your ESP32 firmware to match your server:
```
GET  /update_sensor_data?temperature=25&humidity=60&soil_moisture=45
GET  /api/control_data
GET  /api/dashboard_data
```


