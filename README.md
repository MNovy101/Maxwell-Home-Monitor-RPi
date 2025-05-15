
## Maxwell Home Energy Monitor (MicroPython on ESP32)

A lightweight MicroPython application for real-time residential energy monitoring using a split-core CT sensor and Firebase Realtime Database. Includes local JSON backup on the ESP32’s filesystem.

---

### 1. Features

* **True-RMS Current Measurement** via CT sensor
* **Power Calculation** (using fixed mains voltage & PF)
* **Live Upload** to Firebase Realtime Database via REST API
* **Local Backup** of every record in JSON (`energy_backup.json`)
* **Hardware Alerts** (LED/buzzer) when usage exceeds threshold
* **Configurable** via constants in `main.py`

---

### 2. Hardware Requirements

* **ESP32 Development Board** (e.g. ESP32-WROOM)
* **PZCT-02 Split-Core CT Sensor** (100 A)
* **Burden Resistor**: 10 Ω, ¼ W
* **Breadboard / Wiring**
* **Optional Alert Device** (LED or buzzer on GPIO 5)
* **5 V DC Power Supply** (for ESP32 VIN and sensor VCC)

---

### 3. Software Prerequisites

* **MicroPython Firmware** for ESP32 (latest stable)
* **esptool.py** (to flash firmware)
* **ampy** or **rshell** or **Thonny** (to copy files)
* **Firebase Realtime Database** project & REST permissions

---

### 4. Firebase Setup

1. In your Firebase console, create a **Realtime Database**.
2. Under **Rules**, replace with:

   ```json
   {
     "rules": {
       "energy_data": {
         ".read":  true,
         ".write": true,
         ".indexOn": ["timestamp"],
         "$timestamp": {
           ".validate": "newData.hasChildren(['voltage','current','power'])",
           "voltage": {".validate":"newData.isNumber()"},
           "current": {".validate":"newData.isNumber()"},
           "power":   {".validate":"newData.isNumber()"}
         }
       },
       "alerts": {
         ".read": true,
         ".write": true,
         "$alert_id": {
           ".validate": "newData.hasChildren(['state','timestamp'])",
           "state":     {".validate":"newData.isString() && (newData.val()=='triggered'||newData.val()=='cleared')"},
           "timestamp": {".validate":"newData.isNumber()"}
         }
       }
     }
   }
   ```
3. Note your **Database URL** (e.g. `https://<project>.firebaseio.com`).

---

### 5. Flashing MicroPython

1. **Install esptool**:

   ```bash
   pip install esptool
   ```
2. **Erase** existing flash and **write** firmware:

   ```bash
   esptool.py --chip esp32 erase_flash
   esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-*.bin
   ```

---

### 6. Deploying Firmware

Using **ampy** (example):

```bash
pip install adafruit-ampy
ampy --port /dev/ttyUSB0 put boot.py
ampy --port /dev/ttyUSB0 put main.py
```

Alternatively, use **Thonny**: open `boot.py` and `main.py` and save to device.

---

### 7. Configuration

* **boot.py**

  * Set your Wi-Fi SSID and password.
* **main.py**

  * Update `FIREBASE_URL` to your database URL.
  * Adjust constants as needed:

    ```python
    BURDEN_OHMS      = 10.0
    CT_RATIO         = 2000
    MAINS_VOLTAGE    = 230.0
    POWER_FACTOR     = 0.95
    SAMPLE_COUNT     = 40
    POWER_THRESHOLD  = 1500
    ALERT_PIN        = 5
    BACKUP_FILE      = '/energy_backup.json'
    ```

---

### 8. Operation

1. **Reset ESP32** – it will auto-connect to Wi-Fi.
2. **boot.py** lights on-board LED to indicate connection.
3. **main.py** enters continuous loop:

   * Samples CT sensor, computes RMS current.
   * Calculates real-time power.
   * Appends record (timestamp, voltage, current, power) to `energy_backup.json`.
   * PUTs to `/<timestamp>.json` under `/energy_data` in Firebase.
   * Triggers alert hardware if power > threshold, and logs under `/alerts`.

---

### 9. Troubleshooting

* **No Wi-Fi?** Check SSID/password and SPIFFS filesystem.
* **Firebase errors?** Check REST URL and open database rules.
* **Backup file too large?** Mount external SPIFFS or periodically clear file.
* **Sensor readings noisy?** Add 0.1 µF capacitors at sensor outputs.
