import RPi.GPIO as GPIO
import time, math
from mpu9255 import MPU9255
import statistics
#from statistics import mode

vr0 = 12
zf0 = 16
en0 = 20
sp0 = 21
vr1 = 13
zf1 = 6
en1 = 26
sp1 = 19
backward= 0
forward = 1
F_PWM = 1000
dc = 0
maglst = [0,0,0,0,0,0,0,0,0,0]
#-----------------------------------------------------------
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
mpu = MPU9255()
#-----------------------------------------------------------
def setupIO(vr,zf,en,sp,dir, freq, dc):
    GPIO.setup(sp,GPIO.IN)
    GPIO.setup(en,GPIO.OUT)
    GPIO.setup(zf,GPIO.OUT)
    GPIO.setup(vr,GPIO.OUT)
    GPIO.output(en, 1)
    GPIO.output(zf, dir)
    p = GPIO.PWM(vr, freq)
    p.start(dc)
    return p
#------------------------------------------------------------
def rite(channel):
    global cnt0
    cnt0 = cnt0 + 1;
#------------------------------------------------------------
def left(channel):
    global cnt1
    cnt1 = cnt1 + 1;
#------------------------------------------------------------
def most_frequent(List):
    return max(set(List), key = List.count)

p0 = setupIO(vr0,zf0,en0,sp0,backward,F_PWM,dc)
p1 = setupIO(vr1,zf1,en1,sp1,forward,F_PWM,dc)
magcnt = 0
magsum = 0
cnt0 = 0
cnt1 = 0
t_o =time.time()
GPIO.add_event_detect(sp0, GPIO.RISING,callback=rite)
GPIO.add_event_detect(sp1, GPIO.RISING,callback=left)
while 1:
    try:
        mx,my,mz = mpu.AK8963_conv()
        phi = int(math.atan2(mx, my) * 57.29577951)
        if phi < 0:
            phi = 360 + phi
        maglst[magcnt] = phi
        magsum = magsum + phi
        magcnt = (magcnt + 1) % 10
        if magcnt == 0:
            res = statistics.pstdev(maglst)
            if res > 5:
                print  most_frequent(maglst)/9
            else:
                print(magsum / 90)
            magsum = 0
        if cnt0 >= 45 | cnt1 >= 45:
            ocnt0 = cnt0
            ocnt1 = cnt1
            cnt0 = 0
            cnt1 = 0
            now = time.time()
            delta = now - t_o
            t_o = now
            print "Right Pulses/s = ", ocnt0 / delta, "Speed km/h  =", 0.040212 * ocnt0 / delta
            print "Left  Pulses/s = ", ocnt1 / delta, "Speed km/h  =", 0.040212 * ocnt1 / delta
            print " ------------------------------------------------------------------------------"
    except KeyboardInterrupt:
         GPIO.cleanup()
         break
