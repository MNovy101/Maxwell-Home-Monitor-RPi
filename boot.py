# boot.py – runs on every reset; configures filesystem & network
import network
import uos
import esp
import machine

# Enable filesystem if needed
try:
    import littlefs
except:
    pass

# Connect to Wi-Fi
ssid = 'YOUR_SSID'
pw   = 'YOUR_PASSWORD'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    wlan.connect(ssid, pw)
    for _ in range(20):
        if wlan.isconnected():
            break
        machine.idle()
    
# LED on board to indicate networking
led = machine.Pin(2, machine.Pin.OUT)
led.value(1 if wlan.isconnected() else 0)
