#!/usr/bin/micropython

# Based on https://gist.github.com/neomanic/353727073989c5bacd9a11223ba405c3

# See https://docs.micropython.org/en/latest/reference/isr_rules.html#the-emergency-exception-buffer
import micropython
micropython.alloc_emergency_exception_buf(100)

import machine
import picozero
import network
import socket
import time

import secrets
import sentry

SENTRY_CLIENT = sentry.SentryClient(secrets.SENTRY_INGEST, secrets.SENTRY_PROJECT_ID, secrets.SENTRY_KEY)

PULSES = 0
def count_pulses():
    global PULSES
    PULSES += 1

def main() -> None:
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)

    led = picozero.Pin(25, machine.Pin.OUT)
    led.on() # Turn on the onboard LED

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

def main_safe():
    while True:
        try:
            main()
        except KeyboardInterrupt:
            break
        except MemoryError as e:
            print(SENTRY_CLIENT.send_exception(e))

            machine.reset()
        except Exception as e:
            print(SENTRY_CLIENT.send_exception(e))

            time.sleep_ms(1000)
        except:  # noqa
            time.sleep_ms(1000)

main_safe()
