from  mpu9250_i2c import * 
import time
import math

time.sleep(1) # delay necessary to allow mpu9250 to settle
print('recording data')
while 1:
    ax,ay,az,wx,wy,wz = mpu6050_conv() # read and convert mpu6050 data
    mx,my,mz = AK8963_conv() # read and convert AK8963 magnetometer data
    direction = math.atan2(mx,my)*180/3.14159
    print('{}'.format('-'*30))
    print("accel  [g]: x ={0:2.2f} , y ={1:2.2f} , z = {2:2.2f}".format(ax,ay,az))
    print("gyro [dps]: x ={0:2.2f} , y ={1:2.2f} , z = {2:2.2f}".format(wx,wy,wz))
    print("mag   [uT]: x ={0:2.2f} , y ={1:2.2f} , z = {2:2.2f}".format(mx,my,mz))
    print  direction
    print('{}'.format('-'*30))
    time.sleep(1)
