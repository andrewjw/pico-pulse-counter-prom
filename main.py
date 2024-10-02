#!/usr/bin/micropython

# See https://docs.micropython.org/en/latest/reference/isr_rules.html#the-emergency-exception-buffer
import micropython
micropython.alloc_emergency_exception_buf(100)

from machine import Pin
import picozero
import network
import socket

import secrets

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)

LED = Pin(25, Pin.OUT)
LED.on() # Turn on the onboard LED

PULSES = 0
def count_pulses():
    global PULSES
    PULSES += 1

switch = picozero.Switch(13, True, 0.1)
switch.when_activated = count_pulses

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("", 80))
s.listen()

while True:
    conn, addr = s.accept()
    request = conn.recv(1024)

    conn.sendall(
f"""HTTP/1.1 200 OK
Content-Type: text/plain; charset=UTF-8; version=0.0.4
Access-Control-Allow-Origin: *
Connection: close

# HELP watermeter_count Total litres of water used.
# TYPE watermeter_count counter
watermeter_count {PULSES}
""")

    conn.close()

#def irq(pin):
#    micropython.schedule(print_pulse, 0)

#p2 = Pin(13, Pin.IN, Pin.PULL_UP)
#p2.irq(irq, Pin.IRQ_FALLING)

while True:
    pass
