#!/usr/bin/env python3
"""
Maxwell Home Energy Monitor - Raspberry Pi Edition
Features:
- True RMS calculations for accurate measurements
- Batch updates to Firebase Realtime Database
- Hardware alerts via GPIO
- Configurable calibration through JSON
"""

import time
import math
import json
import spidev
import RPi.GPIO as GPIO
from collections import deque
import threading
import sqlite3
import firebase_admin
from firebase_admin import credentials, db

# Configuration
CONFIG_FILE = 'config.json'
FIREBASE_CRED = 'serviceAccountKey.json'
SAMPLES_PER_CYCLE = 40  # Adjust based on mains frequency
ALERT_HYSTERESIS = 5  # Seconds before clearing alert
SQLITE_DB = 'energy_readings.db'

class EnergyMonitor:
    def __init__(self, config):
        self.config = config
        self.ct_ratio = self.config.get('ct_ratio', 2000)
        self.burden = self.config.get('burden_resistor', 10.0)
        self.voltage = self.config.get('mains_voltage', 230.0)
        self.power_factor = self.config.get('power_factor', 0.95)
        self.adc_channel = self.config.get('adc_channel', 0)
        self.alert_pin = self.config.get('alert_pin', 17)
        self.power_threshold = self.config.get('power_threshold', 1500)
        self.firebase_url = self.config.get('firebase_url')
        self.setup_hardware()
        self.firebase_ref = self.init_firebase()
        self.data_buffer = deque(maxlen=300)
        self.alert_state = False
        self.last_alert = 0
        self.init_database()

    def setup_hardware(self):
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 1350000
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.alert_pin, GPIO.OUT)

    def init_firebase(self):
        cred = credentials.Certificate(FIREBASE_CRED)
        firebase_admin.initialize_app(cred, {
            'databaseURL': self.firebase_url
        })
        return db.reference('/energy_data')

    def init_database(self):
        self.conn = sqlite3.connect(SQLITE_DB, check_same_thread=False)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS readings (
                timestamp INTEGER PRIMARY KEY,
                voltage REAL,
                current REAL,
                power REAL
            )
        ''')

    def read_adc(self):
        adc = self.spi.xfer2([1, (8 + self.adc_channel) << 4, 0])
        return ((adc[1] & 3) << 8) + adc[2]

    def read_samples(self, num_samples):
        return [self.read_adc() for _ in range(num_samples)]

    def calculate_rms(self, samples):
        offset = sum(samples) / len(samples)
        squared = [(s - offset) ** 2 for s in samples]
        mean_square = sum(squared) / len(squared)
        voltage = math.sqrt(mean_square) * (3.3 / 1024 / self.burden)
        return voltage

    def calculate_power(self, samples):
        rms_current = self.calculate_rms(samples) * self.ct_ratio
        return rms_current * self.voltage * self.power_factor

    def check_alerts(self, power):
        current_time = time.time()
        if power > self.power_threshold:
            if not self.alert_state or current_time - self.last_alert > ALERT_HYSTERESIS:
                self.trigger_alert(True)
                self.last_alert = current_time
        else:
            if self.alert_state and current_time - self.last_alert > ALERT_HYSTERESIS:
                self.trigger_alert(False)

    def trigger_alert(self, state):
        self.alert_state = state
        GPIO.output(self.alert_pin, state)
        db.reference('/alerts').push({
            'timestamp': int(time.time()),
            'state': 'triggered' if state else 'cleared'
        })

    def store_data(self, data):
        ts = data['timestamp']
        voltage = data['voltage']
        current = data['current']
        power = data['power']
        self.conn.execute('''
            INSERT INTO readings (timestamp, voltage, current, power)
            VALUES (?, ?, ?, ?)
        ''', (ts, voltage, current, power))
        self.conn.commit()

    def run(self):
        try:
            while True:
                samples = self.read_samples(SAMPLES_PER_CYCLE)
                power = self.calculate_power(samples)
                current = power / self.voltage
                data = {
                    'timestamp': int(time.time()),
                    'voltage': self.voltage,
                    'current': round(current, 3),
                    'power': round(power, 2)
                }
                self.data_buffer.append(data)
                self.store_data(data)
                self.check_alerts(power)
                if len(self.data_buffer) >= 60:
                    batch = list(self.data_buffer)
                    self.data_buffer.clear()
                    threading.Thread(
                        target=lambda: self.firebase_ref.update({str(d['timestamp']): d for d in batch})
                    ).start()
                time.sleep(1.0 / SAMPLES_PER_CYCLE)
        except KeyboardInterrupt:
            print("Shutdown requested")
        finally:
            self.spi.close()
            GPIO.cleanup()
            self.conn.close()

if __name__ == '__main__':
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    monitor = EnergyMonitor(config)
    monitor.run()
