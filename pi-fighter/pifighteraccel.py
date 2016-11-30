import smbus

# Power management registers
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c


def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def dist(a,b):
    return math.sqrt((a*a)+(b*b))

def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)

def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)

def GetScaledAccelValues():
	try:
		# Grab Accelerometer Data 
		accel_xout = read_word_2c(0x3b)
		accel_yout = read_word_2c(0x3d)
		accel_zout = read_word_2c(0x3f)
	except:
		print("** Read failed - assume 0 accel")
		accel_xout =0
		accel_yout =0
		accel_zout =0
		
	ScaledAccel = [accel_xout / 16384.0 *8, accel_yout / 16384.0 *8, accel_zout / 16384.0*8]
	return ScaledAccel


	
# Start talking to accelerometer - standard I2C stuff.  
bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
address = 0x68       # This is the address value read via the i2cdetect command

# Now wake the 6050 up as it starts in sleep mode
bus.write_byte_data(address, power_mgmt_1, 0)

# Write the setup to the accelerometer - value of 3 in AFS_SEL gives accel range of 16g.  The register to use is 1C (28 decimal)
bus.write_byte_data(address, 0x1C, 0b00011000)

# Adjust sensitivity of accelerometer to maximum of 16g.  

''' Not using gyro yet. - Not sure if I need/want it.  
print( "gyro data")
print( "---------")

gyro_xout = read_word_2c(0x43)
gyro_yout = read_word_2c(0x45)
gyro_zout = read_word_2c(0x47)

print ("gyro_xout: ", gyro_xout, " scaled: ", (gyro_xout / 131))
print ("gyro_yout: ", gyro_yout, " scaled: ", (gyro_yout / 131))
print ("gyro_zout: ", gyro_zout, " scaled: ", (gyro_zout / 131))

print ("accelerometer data")
print ("------------------")
'''

