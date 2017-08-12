# Standard modules
import queue
import subprocess
import os
import datetime
import logging
import configparser

# Third Party Modules
import pigpio


"""
This bit just gets the pigpiod daemon up and running if it isn't already.

The pigpio daemon accesses the Raspberry Pi GPIO.  
"""

p = subprocess.Popen(['pgrep', '-f', 'pigpiod'], stdout=subprocess.PIPE)
out, err = p.communicate()

if len(out.strip()) == 0:
    os.system("sudo pigpiod")

""" 
End of getting pigpiod running.
"""

# Queue to send Rumble Requests.
RumbleQ = queue.Queue()

# HARD - CODED address of Accelerometer the Pi is using.
# This is the address value read via the i2cdetect command
accel_address = 0x68

# Required power management codes for the accelerometer.
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

# Set up the Pigpio Pi.  This is how pigpio is set up.
pi = pigpio.pi()


# Setting up logging - add in time to it. Create a filename using time functions
Now = datetime.datetime.now()
LogFileName = "PiTrainer_" + Now.strftime("%y_%m_%d_%H%M") + ".log"

# Sets up the logging - no special settings.
logging.basicConfig(filename=LogFileName, level=logging.DEBUG)

# Setting up to read config file
config_file = configparser.RawConfigParser()
config_file.read('PiTrainer.cfg')

# Get the sampling rate to use
SAMPLE_SLEEP = config_file.getint('TIMING', 'SAMPLE_SLEEP')

# Get Display Sample - how often to update the display based on how many samples are taken before displaying
DISPLAY_FREQ = config_file.getint('TIMING', 'DISPLAY_FREQ')

# Get Skip Threshold - the g force that has to be exceeded to register one skip count.
SKIP_THRESHOLD = config_file.getint('THRESHOLDS', 'SKIP_THRESHOLD')

# Get Server Information
SERVER_HOST = config_file['SERVER']['SERVER_HOST']
SERVER_PORT = int(config_file['SERVER']['SERVER_PORT'])
