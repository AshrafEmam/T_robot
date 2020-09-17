# this is to be saved in the local folder under the name "mpu9250_i2c.py"
# it will be used as the I2C controller and function harbor for the project 
# refer to datasheet and register map for full explanation

import smbus,time

MPU6050_ADDR = 0x68
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
ACCEL_CONFIG = 0x1C
INT_PIN_CFG = 0x37
INT_ENABLE = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
TEMP_OUT_H = 0x41
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47
# AK8963 registers
AK8963_ADDR = 0x0C
AK8963_ST1 = 0x02
HXH = 0x04
HYH = 0x06
HZH = 0x08
AK8963_ST2 = 0x09
AK8963_CNTL = 0x0A
mag_sens = 0.149536       # 4900.0   magnetometer sensitivity: 4800 uT
#=========================================================================
class MPU9255(object):
    '''
        Simple MPU-6050 implementation
   '''

    def __init__(self):
    # start comm with i2c bus
        self.bus = smbus.SMBus(1)
    # alter sample rate (stability)
        samp_rate_div = 0 # sample rate = 8 kHz/(1+samp_rate_div) 
        self.bus.write_byte_data(MPU6050_ADDR, SMPLRT_DIV, samp_rate_div)
        time.sleep(0.1)
    # reset all sensors
        self.bus.write_byte_data(MPU6050_ADDR,PWR_MGMT_1,0x80)
        time.sleep(0.1)
    # power management and crystal settings
        self.bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0x01)
        time.sleep(0.1)
    #Write to Configuration register
        self.bus.write_byte_data(MPU6050_ADDR, CONFIG, 0)
        time.sleep(0.1)
    #Write to Gyro configuration register
        gyro_config_sel = [0b00000,0b010000,0b10000,0b11000] # byte registers
        gyro_config_vals = [250.0,500.0,1000.0,2000.0] # degrees/sec
        gyro_indx = 0
        self.bus.write_byte_data(MPU6050_ADDR, GYRO_CONFIG, int(gyro_config_sel[gyro_indx]))
        time.sleep(0.1)
    #Write to Accel configuration register
        accel_config_sel = [0b00000,0b01000,0b10000,0b11000] # byte registers
        accel_config_vals = [2.0,4.0,8.0,16.0] # g (g = 9.81 m/s^2)
        accel_indx = 0                            
        self.bus.write_byte_data(MPU6050_ADDR, ACCEL_CONFIG, int(accel_config_sel[accel_indx]))
        time.sleep(0.1)
        self.gyro_sens  = gyro_config_vals[gyro_indx] / 32768
        self.accel_sens = accel_config_vals[accel_indx] / 32768
    # interrupt register (related to overflow of data [FIFO])
        self.bus.write_byte_data(MPU6050_ADDR, INT_ENABLE, 1)
        time.sleep(0.1)
        self.AK8963_start()
#----------------------------------------------------------------
    def read_raw_bits(self, register):
    # read accel and gyro values
        self.high = self.bus.read_byte_data(MPU6050_ADDR, register)
        self.low = self.bus.read_byte_data(MPU6050_ADDR, register+1)
    # combine higha and low for unsigned bit value
        self.value = ((self.high << 8) | self.low)
    # convert to +- value
        if(self.value > 32768):
            self.value -= 65536
        return self.value
#----------------------------------------------------------------
    def mpu6050_conv(self):
    # raw acceleration bits
    # print "read acc"
        self.acc_x = self.read_raw_bits(ACCEL_XOUT_H)
        self.acc_y = self.read_raw_bits(ACCEL_YOUT_H)
        self.acc_z = self.read_raw_bits(ACCEL_ZOUT_H)
    # raw gyroscope bits
    # print "read gyro"
        self.gyro_x = self.read_raw_bits(GYRO_XOUT_H)
        self.gyro_y = self.read_raw_bits(GYRO_YOUT_H)
        self.gyro_z = self.read_raw_bits(GYRO_ZOUT_H)
    # print "calculating"
    # convert to acceleration in g and gyro dps
        self.a_x = self.acc_x * self.accel_sens
        self.a_y = self.acc_y * self.accel_sens
        self.a_z = self.acc_z * self.accel_sens
        self.w_x = self.gyro_x * self.gyro_sens
        self.w_y = self.gyro_y * self.gyro_sens
        self.w_z = self.gyro_z * self.gyro_sens
##    temp = ((t_val)/333.87)+21.0 # uncomment and add below in return
        return self.a_x,self.a_y,self.a_z,self.w_x,self.w_y,self.w_z
#---------------------------------------------------------------
    def AK8963_start(self):
        self.bus.write_byte_data(MPU6050_ADDR,INT_PIN_CFG, 0x02)
        time.sleep(0.1)
        self.bus.write_byte_data(AK8963_ADDR,AK8963_CNTL,0x16)
        time.sleep(0.1)
#---------------------------------------------------------------
    def AK8963_reader(self, register):
    # read magnetometer values
        low = self.bus.read_byte_data(AK8963_ADDR, register-1)
        high = self.bus.read_byte_data(AK8963_ADDR, register)
    # combine higha and low for unsigned bit value
        value = ((high << 8) | low)
    # convert to +- value
        if(value > 32768):
             value -= 65536
        return value
#---------------------------------------------------------------
    def AK8963_conv(self):
    # raw magnetometer bits
        while 1:
            stu = self.bus.read_byte_data(AK8963_ADDR,AK8963_ST1)
            #print stu
            if (stu & 0x01) == 1:
                break
        self.mag_x = self.AK8963_reader(HXH)
        self.mag_y = self.AK8963_reader(HYH)
        self.mag_z = self.AK8963_reader(HZH)
        self.bus.read_byte_data(AK8963_ADDR,AK8963_ST2)
    #convert to magnetometer in uT
        self.m_x = self.mag_x * mag_sens
        self.m_y = self.mag_y * mag_sens
        self.m_z = self.mag_z * mag_sens
        return self.m_x,self.m_y,self.m_z
