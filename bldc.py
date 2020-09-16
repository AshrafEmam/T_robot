import RPi.GPIO as GPIO
import time

vr = 12
zf = 16
en = 20
sp = 21
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)  

GPIO.setup(sp,GPIO.IN)
GPIO.setup(en,GPIO.OUT)
GPIO.setup(zf,GPIO.OUT)
GPIO.setup(vr,GPIO.OUT)
GPIO.output(en, 1)
GPIO.output(zf, 0)
p = GPIO.PWM(vr, 1000)
p.start(18)

count = 0

def my_callback (channel):
    global count
    count = count + 1;
#    print (count)
oldtime =time.time()
GPIO.add_event_detect(sp, GPIO.RISING,callback=my_callback)
while 1:
    try:
        if count >= 45:
            oldcount = count
            count = 0
            ztime = time.time()
            delta = ztime - oldtime
            oldtime = ztime
            print "Pulses/s = ",oldcount/delta, "Speed km/h  =", 0.040212*oldcount/delta
    except KeyboardInterrupt:
         GPIO.cleanup()
         break
