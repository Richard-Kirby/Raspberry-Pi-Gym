# Third part packages.
import smbus  # need to get smbus library by the following command $sudo apt-get install python-smbus

# Project related packages
import config.config as config


# Class to manage the I2C accelerometer
class I2C_Accelorometer:

    # Set up the accelerometer for use.  This involves sending it the right
    # power management codes to wake it up and setting the sensitivity.
    def __init__(self):
        # Power management registers for accelerometer

        # Start talking to accelerometer - standard I2C stuff.
        self.bus = smbus.SMBus(1)  # or bus = smbus.SMBus(1) for Revision 2 boards

        # Now wake the 6050 up as it starts in sleep mode
        self.bus.write_byte_data(config.accel_address, config.power_mgmt_1, 0)

        # Write the setup to the accelerometer - value of 3 in AFS_SEL gives accel range of 16g.
        # The register to use is 1C (28 decimal)
        self.bus.write_byte_data(config.accel_address, 0x1C, 0b00011000)

    # Standard reading functions for Accelerometer
    def read_byte(self,adr):
        return self.bus.read_byte_data(config.accel_address, adr)

    def read_word(self,adr):
        high = self.bus.read_byte_data(config.accel_address, adr)
        low = self.bus.read_byte_data(config.accel_address, adr + 1)
        val = (high << 8) + low
        return val

    def read_word_2c(self,adr):
        val = self.read_word(adr)
        if (val >= 0x8000):
            return -((65535 - val) + 1)
        else:
            return val


    def dist(self,a, b):
        return math.sqrt((a * a) + (b * b))


    def get_y_rotation(self,x, y, z):
        radians = math.atan2(x, dist(y, z))
        return -math.degrees(radians)


    def get_x_rotation(self,x, y, z):
        radians = math.atan2(y, dist(x, z))
        return math.degrees(radians)

    # Grabs and scales the accelerometer output.
    def get_scaled_accel_values(self):
        try:
            # Grab Accelerometer Data
            accel_xout = self.read_word_2c(0x3b)
            accel_yout = self.read_word_2c(0x3d)
            accel_zout = self.read_word_2c(0x3f)
        except:
            print("** Read failed - assume 0 accel")
            accel_xout = 0
            accel_yout = 0
            accel_zout = 0
            raise

        scaled_accel = [accel_xout / 16384.0 * 8, accel_yout / 16384.0 * 8, accel_zout / 16384.0 * 8]
        return scaled_accel


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
