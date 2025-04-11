# Maxwell Home Energy Monitor

A Python-based home energy monitoring system for Raspberry Pi that supports:

- True RMS current measurement
- Real-time power calculation
- Firebase Realtime Database integration
- Hardware-based alerts
- Configurable calibration

---

## Prerequisites

### Hardware

- Raspberry Pi (Model 3 or newer)
- Current transformer (CT) sensor
- Burden resistor (e.g., 10Ω)
- Optional: MLX90614 sensor for temperature readings
- Optional: RGB LED or other indicators for alerts

### Software

- Raspberry Pi OS (latest version)
- Python 3.x
- Pip package manager

---

## Installation

### 1. Update System Packages


```bash
sudo apt update && sudo apt upgrade -y
```


### 2. Install Python Dependencies


```bash
sudo apt install python3-pip python3-spidev python3-rpi.gpio -y
pip3 install firebase-admin
```


### 3. Clone the Repository


```bash
git clone https://github.com/yourusername/maxwell-monitor.git
cd maxwell-monitor
```


### 4. Configure the System

Create a `config.json` file in the project directory with the following structure:


```json
{
  "ct_ratio": 2000,
  "burden_resistor": 10.0,
  "mains_voltage": 230.0,
  "power_factor": 0.95,
  "power_threshold": 1500,
  "alert_pin": 17,
  "adc_channel": 0,
  "firebase_url": "https://your-project.firebaseio.com/"
}
```


- Replace `"firebase_url"` with your Firebase Realtime Database URL.

---

## Firebase Integration

### 1. Set Up Firebase Project

- Go to the [Firebase Console](https://console.firebase.google.com/) and create a new project.
- Navigate to **Build > Realtime Database** and create a new database.
- Set the database rules to allow read/write access as needed.

### 2. Generate Service Account Key

- In the Firebase Console, go to **Project Settings > Service Accounts**.
- Click on **Generate New Private Key** and download the JSON file.
- Save this file as `serviceAccountKey.json` in the project directory.

### 3. Secure the Key

- Add `serviceAccountKey.json` to your `.gitignore` file to prevent it from being committed to version control.

---

## Running the Monitor

Execute the main script:


```bash
python3 maxwell_monitor.py
```


The script will:

- Calibrate the sensors
- Continuously read current and voltage
- Calculate power consumption
- Send data to Firebase
- Trigger alerts if power exceeds the threshold

---

## Additional Resources

- [Firebase Admin SDK Documentation](https://firebase.google.com/docs/admin/setup)
- [Raspberry Pi GPIO Documentation](https://www.raspberrypi.org/documentation/usage/gpio/)
- [Pyrebase GitHub Repository](https://github.com/thisbejim/Pyrebase)
