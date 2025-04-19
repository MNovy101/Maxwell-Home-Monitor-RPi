# **Maxwell Home Energy Monitor**  
A Python-based home energy monitoring system for Raspberry Pi that supports:

- True RMS current measurement
- Real-time power calculation
- Firebase Realtime Database integration
- Hardware-based alerts
- Configurable calibration

---

## **Prerequisites**

### **Hardware**  
- Raspberry Pi (Model 3 or newer)  
- Current transformer (CT) sensor  
- Burden resistor

### **Software**  
- Raspberry Pi OS (latest version)  
- Python 3.x  
- Pip package manager  

---

## **Installation**

### **1. Update System Packages**  
Run the following command to update the system packages:  
```bash
sudo apt update && sudo apt upgrade -y
```

### **2. Install Python Dependencies**  
Install the required Python dependencies:  
```bash
sudo apt install python3-pip python3-spidev python3-rpi.gpio -y
pip3 install firebase-admin
```

### **3. Clone the Repository**  
Clone the repository containing the code:  
```bash
git clone https://github.com/yourusername/maxwell-monitor.git
cd maxwell-monitor
```

### **4. Update Secret Key**  
Due to security concerns, the Secret Key will need to be requested and added manually.

## **Running the Monitor**

### **1. Execute the Main Script**  
Run the main Python script to start the energy monitoring system:  
```bash
python3 maxwell_monitor.py
```

### **What the Script Does:**  
- **Calibrates the sensors** based on the settings in `config.json`.  
- **Continuously reads current and voltage** through the connected ADC (Analog-to-Digital Converter).  
- **Calculates power consumption** based on the sensor data.  
- **Sends data to Firebase** to keep track of energy usage in real-time.  
- **Triggers alerts** via GPIO if the power consumption exceeds the defined threshold in `config.json`.

---

## **Additional Resources**

- 📄 [Firebase Admin SDK Documentation](https://firebase.google.com/docs/database/admin/start)  
- 🔌 [Raspberry Pi GPIO Documentation](https://www.raspberrypi.org/documentation/usage/gpio/)  
- 🌐 [Pyrebase GitHub Repository](https://github.com/thisbejim/Pyrebase)  
