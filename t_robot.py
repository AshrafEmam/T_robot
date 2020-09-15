import RPi.GPIO as GPIO
import time
import sys
import evdev
from evdev import InputDevice, categorize, ecodes

en0 = 20
vr0 = 12
zf0 = 16
sg0 = 21
en1 = 6
vr1 = 13
zf1 = 19
sg1 = 26
trig = 23
echo = 24
gang = 0
# ----------------------------------------------------------------
try:
    while 1:
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        devPath = ''
        for device in devices:
            devName = device.name
            if devName.find('Xbox') != -1:
                devPath = device.path
        if devPath != '':
            break
except KeyboardInterrupt:
    sys.exit()
# ------------------------- Setting GPIO  --------------------------
gamepad = InputDevice(devPath)
GPIO.setmode(GPIO.BCM)
GPIO.setup(en0, GPIO.OUT)
GPIO.setup(vr0, GPIO.OUT)
GPIO.setup(zf0, GPIO.OUT)
GPIO.setup(sg0, GPIO.IN)
p0 = GPIO.PWM(vr0, 1000)

GPIO.setup(en1, GPIO.OUT)
GPIO.setup(vr1, GPIO.OUT)
GPIO.setup(zf1, GPIO.OUT)
GPIO.setup(sg1, GPIO.IN)
p1 = GPIO.PWM(vr1, 1000)

p0.start(0)
p1.start(0)

GPIO.output(en0, GPIO.LOW)
GPIO.output(en1, GPIO.LOW)

GPIO.output(zf0, GPIO.LOW)
GPIO.output(zf1, GPIO.HIGH)

dc = 0

p0.ChangeDutyCycle(dc)
p1.ChangeDutyCycle(dc)

GPIO.output(en0, GPIO.HIGH)
GPIO.output(en1, GPIO.HIGH)
reverse = -1


# --------------------- functions -----------------------
def xbox_in(jcode, jval, gang, reverse):
    if jcode == 9:
        dc = jval / 100
        p0.ChangeDutyCycle(dc)
        if gang == 1:
            p1.ChangeDutyCycle(dc)
    elif jcode == 10:
        dc = jval / 100
        p1.ChangeDutyCycle(dc)
        if (gang == 1):
            p0.ChangeDutyCycle(dc)
    elif jcode == 17:  # reverse/forward
        if reverse != jval:
            p0.ChangeDutyCycle(0)
            p1.ChangeDutyCycle(0)
            time.sleep(0.5)
            if jval == 1:
                GPIO.output(zf0, GPIO.HIGH)  # reverse
                GPIO.output(zf1, GPIO.LOW)
                reverse = jval
            elif jval == -1:
                GPIO.output(zf0, GPIO.LOW)  # forward
                GPIO.output(zf1, GPIO.HIGH)
                reverse = jval
    elif jcode == 16:  # right/left
        if jval == -1:
            dc = 3
            p0.ChangeDutyCycle(0)
            p1.ChangeDutyCycle(0)
            time.sleep(0.5)
            GPIO.output(zf0, GPIO.LOW)  #
            GPIO.output(zf1, GPIO.LOW)
            p0.ChangeDutyCycle(dc)
            p1.ChangeDutyCycle(dc)
        elif jval == 1:
            dc = 3
            p0.ChangeDutyCycle(0)
            p1.ChangeDutyCycle(0)
            time.sleep(0.5)
            GPIO.output(zf0, GPIO.HIGH)
            GPIO.output(zf1, GPIO.HIGH)
            p0.ChangeDutyCycle(dc)
            p1.ChangeDutyCycle(dc)
        else:
            time.sleep(0.25)
            GPIO.output(zf0, GPIO.LOW)
            GPIO.output(zf1, GPIO.HIGH)
            p0.ChangeDutyCycle(0)
            p1.ChangeDutyCycle(0)
    elif jcode == 305:  # disable motors
        GPIO.output(en0, GPIO.LOW)
        GPIO.output(en1, GPIO.LOW)
    elif jcode == 304:  # enable motors
        GPIO.output(en0, GPIO.HIGH)
        GPIO.output(en1, GPIO.HIGH)
    elif jcode == 310:
        if jval == 1:
            if gang == 0:
                gang = 1
            else:
                gang = 0
    return (gang, reverse)


# -------------------------------------------------------
try:
    while 1:
        for event in gamepad.read_loop():
            (gang, reverse) = xbox_in(event.code, event.value, gang, reverse)
        time.sleep(0.01)
except KeyboardInterrupt:
    p0.stop()
    p1.stop()
    GPIO.output(en0, GPIO.LOW)
    GPIO.output(en1, GPIO.LOW)
    GPIO.cleanup()
    sys.exit()
