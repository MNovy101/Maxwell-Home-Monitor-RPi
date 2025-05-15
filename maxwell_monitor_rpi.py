# main.py – Maxwell Home Monitor firmware

import time, ujson, math
import urequests as requests
from machine import ADC, Pin

# --- Configuration ---
FIREBASE_URL     = 'https://maxwell-home-power-monitor-default-rtdb.firebaseio.com'
CT_ADC_PIN       = 34         # ADC1_CH6 on ESP32
BURDEN_OHMS      = 10.0
CT_RATIO         = 2000       # per hardware
MAINS_VOLTAGE    = 230.0
POWER_FACTOR     = 0.95
SAMPLE_COUNT     = 40         # per cycle
BACKUP_FILE      = '/energy_backup.json'
ALERT_PIN        = 5          # Optional external LED/buzzer
POWER_THRESHOLD  = 1500       # W
ALERT_HYSTERESIS = 5          # s

# --- Hardware init ---
adc        = ADC(Pin(CT_ADC_PIN))
adc.atten(ADC.ATTN_11DB)       # full 3.3V range
alert_out  = Pin(ALERT_PIN, Pin.OUT)

# Load or init backup
try:
    with open(BACKUP_FILE) as f:
        backup = ujson.load(f)
except:
    backup = []

last_alert = 0
alert_state = False

def measure_rms():
    vals = []
    for _ in range(SAMPLE_COUNT):
        raw = adc.read()
        vals.append(raw)
        time.sleep_ms(1)
    avg = sum(vals) / len(vals)
    sq = sum((v - avg) ** 2 for v in vals) / len(vals)
    voltage_adc = math.sqrt(sq) * (3.3 / 4095)
    current_amp = voltage_adc / BURDEN_OHMS * CT_RATIO
    return current_amp

def push_firebase(record):
    url = FIREBASE_URL + '/energy_data/{}.json'.format(record['timestamp'])
    headers = {'Content-Type':'application/json'}
    try:
        requests.put(url, data=ujson.dumps({
            'voltage': record['voltage'],
            'current': record['current'],
            'power':   record['power']
        }), headers=headers)
    except:
        pass  # network error

def trigger_alert(state):
    global alert_state, last_alert
    alert_state = state
    alert_out.value(1 if state else 0)
    ts = int(time.time() * 1000)
    url = FIREBASE_URL + '/alerts.json'
    try:
        requests.post(url, data=ujson.dumps({
            'timestamp': ts,
            'state': 'triggered' if state else 'cleared'
        }))
    except:
        pass
    last_alert = time.time()

def main():
    global backup, last_alert, alert_state
    while True:
        now = time.time()
        ts = int(now * 1000)
        i = measure_rms()
        p = i * MAINS_VOLTAGE * POWER_FACTOR
        record = {'timestamp': ts,
                  'voltage': MAINS_VOLTAGE,
                  'current': round(i, 3),
                  'power':   round(p, 2)}
        # Local backup
        backup.append(record)
        try:
            with open(BACKUP_FILE, 'w') as f:
                ujson.dump(backup, f)
        except:
            pass
        # Firebase
        push_firebase(record)
        # Alert logic
        if p > POWER_THRESHOLD and (not alert_state or now - last_alert > ALERT_HYSTERESIS):
            trigger_alert(True)
        elif alert_state and p <= POWER_THRESHOLD and now - last_alert > ALERT_HYSTERESIS:
            trigger_alert(False)
        time.sleep(1)

if __name__=='__main__':
    main()
