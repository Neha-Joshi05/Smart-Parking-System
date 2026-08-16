# 🅿️ Smart Parking System using Ultrasonic Sensors

> **An Embedded Systems project that simulates a real-time Smart Parking System using HC-SR04 Ultrasonic Sensors, Arduino/ESP32 and a stunning interactive nude+dark themed Streamlit dashboard!**

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![Embedded](https://img.shields.io/badge/Embedded-Systems-orange)
![Arduino](https://img.shields.io/badge/Arduino-UNO%2FESP32-teal)
![Plotly](https://img.shields.io/badge/Plotly-Interactive-purple)
![Simulation](https://img.shields.io/badge/Simulation-Real--Time-green)

---
# LIVE PROJECT LINK :- https://smart-parking-system-v8xg.onrender.com

## 📌 Project Overview

A complete **Smart Parking System** that includes:
- 📡 **HC-SR04 Ultrasonic Sensor** simulation
- 🚗 **Real-time slot detection** (Occupied/Available)
- 🗺️ **Live parking slot heatmap**
- 📊 **Revenue & traffic analytics**
- 🚨 **Smart alert system**
- ⚙️ **Manual vehicle entry/exit management**
- 🔒 **Slot reservation system**
- 📡 **Sensor health monitoring**
- 🎨 **Elite nude + dark themed dashboard**
- 💾 **Arduino/ESP32 code included**

**Industry relevance:** Used by Siemens, Bosch, Cisco,
Smart City projects, Shopping Malls, Airports,
Hospitals and Universities for automated parking.

---

## 🗂️ Folder Structure

```
Smart-Parking-System/
├── simulation/
│   ├── sensor.py              # HC-SR04 sensor simulation
│   ├── vehicle.py             # Vehicle simulation
│   └── parking_simulator.py   # Main parking lot engine
├── src/
│   ├── parking_manager.py     # Business logic
│   ├── analytics.py           # Charts & visualizations
│   └── alerts.py              # Smart alert system
├── arduino/
│   ├── smart_parking.ino      # Arduino main code
│   └── config.h               # Hardware config
├── data/                      # Data storage
├── outputs/                   # Generated outputs
├── assets/                    # Images & assets
├── dashboard.py               # Streamlit dashboard
├── main.py                    # CLI interface
├── requirements.txt
└── README.md
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11 |
| Dashboard | Streamlit |
| Visualization | Plotly |
| Data | Pandas, NumPy |
| Simulation | Faker, Custom Engine |
| Hardware | Arduino UNO / ESP32 |
| Sensor | HC-SR04 Ultrasonic |
| Protocol | UART / WiFi (ESP32) |

---

## 📡 HC-SR04 Ultrasonic Sensor

```
Specifications:
├── Range         : 2cm to 400cm
├── Accuracy      : ±3mm
├── Trigger Pulse : 10µs
├── Working Freq  : 40Hz
├── Beam Angle    : 15°
└── Threshold     : < 20cm = Occupied

Formula:
Distance = (Echo Time × Speed of Sound) / 2
Speed of Sound = 343 m/s = 0.0343 cm/µs
```

### How it Works:
```
Ultrasonic Sensor
      │
      ▼ Trigger Pulse (10µs)
      │
      ▼ Sound Wave Emitted (40kHz)
      │
      ▼ Echo Received
      │
      ▼ Distance = (Time × 0.0343) / 2
      │
      ▼ Distance < 20cm?
     / \
   YES   NO
    │     │
    ▼     ▼
Occupied Available
    │     │
    ▼     ▼
Red LED  Green LED
    │     │
    ▼     ▼
LCD/OLED Display Update
    │
    ▼
Available Count Updated
```

---

## 🔌 Hardware Components

| Component | Quantity | Purpose |
|-----------|---------|---------|
| Arduino UNO / ESP32 | 1 | Main microcontroller |
| HC-SR04 Ultrasonic | 4-12 | Slot detection |
| LED (Red) | 4-12 | Occupied indicator |
| LED (Green) | 4-12 | Available indicator |
| LCD 16×2 / OLED | 1 | Display |
| Buzzer | 1 | Entry/Exit alert |
| Servo Motor | 1 | Entry gate |
| Resistors (220Ω) | Multiple | LED current limiting |
| Jumper Wires | Multiple | Connections |
| Breadboard | 1 | Prototyping |

---

## 🔌 Circuit Connections

```
HC-SR04 Sensor → Arduino UNO:
├── VCC   → 5V
├── GND   → GND
├── TRIG  → Digital Pin 2/4/6/8
└── ECHO  → Digital Pin 3/5/7/9

LED Indicators:
├── Red LED   → Digital Pin 10 (via 220Ω)
└── Green LED → Digital Pin 11 (via 220Ω)

LCD 16×2 (I2C):
├── VCC → 5V
├── GND → GND
├── SDA → A4
└── SCL → A5

Buzzer:
└── + → Digital Pin 12

Servo (Entry Gate):
└── Signal → Digital Pin 13
```

---

## 🚀 Getting Started

### Software (Python Dashboard)

```bash
# Clone repo
git clone  https://github.com/Neha-Joshi05/Smart-Parking-System.git
git push -u origin main
cd Smart-Parking-System

# Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run dashboard
python -m streamlit run dashboard.py
```

Open: **http://localhost:8501**

### Hardware (Arduino)

1. Open `arduino/smart_parking.ino` in Arduino IDE
2. Install required libraries:
   - `LiquidCrystal_I2C`
   - `Servo`
3. Select board: **Arduino UNO** or **ESP32**
4. Upload code
5. Open Serial Monitor (9600 baud)

---

## 📊 Dashboard Pages

| Tab | Features |
|-----|---------|
| 🗺️ Live Map | Heatmap, interactive slot grid, alerts, event log |
| 📊 Analytics | Revenue chart, vehicle pie, weekly trend, projections |
| 🚗 Vehicles | Currently parked, history table |
| 📡 Sensors | HC-SR04 health monitor, readings, specs |
| ⚙️ Management | Manual entry/exit, slot reservation, system info |

---

## 🎯 Key Features

### Real-time Monitoring
- ✅ Live slot occupancy heatmap
- ✅ Per-floor status tracking
- ✅ Occupancy rate gauge
- ✅ Auto-refresh simulation

### Smart Alerts
- 🔴 Critical: > 90% full
- 🟡 Warning: > 75% full
- ⏰ Long parked: > 8 hours
- 💰 Revenue milestones
- 📡 Sensor fault detection

### Analytics
- 📈 Hourly revenue & traffic
- 🚗 Vehicle type breakdown
- 📅 Weekly revenue trend
- 💰 Revenue projection (daily/monthly/yearly)
- ⏱️ Parking duration stats

### Management
- 🚗 Manual vehicle entry/exit
- 🔒 Slot reservation
- 👤 Vehicle tracking by plate
- 📋 Complete event log

---

## 🏢 Real-World Applications

| Location | Use Case |
|---------|---------|
| 🛍️ Shopping Malls | Customer parking guidance |
| ✈️ Airports | Long-term parking management |
| 🏥 Hospitals | Emergency slot reservation |
| 🏢 Office Buildings | Employee parking system |
| 🏫 Universities | Campus parking automation |
| 🏙️ Smart Cities | IoT-based parking network |
| 🚉 Railway Stations | Commuter parking |
| 🏘️ Residential | Society parking management |

---

## 💡 Embedded Systems Concepts

```
Microcontroller Programming
├── GPIO Control (Digital I/O)
├── PWM for Servo Motor
├── I2C Protocol (LCD)
├── UART Serial Communication
└── Interrupt handling

Sensor Interfacing
├── HC-SR04 Ultrasonic timing
├── Echo pulse measurement
├── Distance calculation formula
└── Threshold-based detection

IoT Concepts (ESP32)
├── WiFi connectivity
├── HTTP REST API
├── Real-time data streaming
└── Web-based monitoring
```

---

## 🎓 Learning Outcomes

- Ultrasonic sensor interfacing
- Embedded C / Arduino programming
- Distance measurement algorithms
- Real-time system design
- IoT sensor networks
- Python simulation development
- Interactive dashboard creation
- Smart city technology concepts

---

## 🏷️ Topics

`python` `embedded-systems` `arduino` `esp32`
`ultrasonic-sensor` `hc-sr04` `smart-parking`
`iot` `streamlit` `plotly` `simulation`
`real-time` `smart-city` `parking-system`

---

## 👤 Author

**Neha Joshi**
- GitHub: [@Neha-Joshi05](https://github.com/Neha-Joshi05/Smart-Parking-System.git)
- LinkedIn: [neha-joshi-0851a2322](https://www.linkedin.com/in/neha-joshi-0851a2322?utm_source=share_via&utm_content=profile&utm_medium=member_android)

---
