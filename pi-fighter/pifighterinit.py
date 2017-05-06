import pifightermatrix as Matrix
import datetime
import logging 
import configparser
import queue

Mode = 0 # Initial Setting - not a real mode
KickButtMode = 1
WorkoutMode =2 

UserName =""

# Create 2 queues for talking between the threads - one for TCP and one for UDP
UDPCommSendQueue = queue.Queue()
UDPCommRecQueue = queue.Queue()
TCPCommSendQueue = queue.Queue()
TCPCommRecQueue = queue.Queue()


def InitialiseSystem():
	global Mode 
	global UserName
	
	#Set up the mode, getting challengers name 
	#UserName = input("Challenger's name:")
	#UserHealthPoints = 200
	#print(UserName + " is not exactly fierce sounding - Can I call you THE Dragon?")

	# Set up the LED Matrix
	Matrix.Setup()
	
	# Ask what mode to be used.
	Mode = input("Desired Mode [1=Fight someone 2= Workout]")

	if (int(Mode) == KickButtMode):
		print("Kick some butt mode!")
	elif (int(Mode)==WorkoutMode):
		print("Workout as too wimpy to fight yet")
	else:
		print("Invalid Mode - must mean Kick Some Butt Mode")
		Mode = KickButtMode

def SetUpLoggingAndConfig():

	global SAMPLE_SLEEP
	global DISPLAY_FREQ
	global STD_PUNCH_WAIT
	global CMD_FLASH_TIME
	global BETWEEN_SEQ_REST
	global SERVER_HOST
	global TCP_PORT
	global UDP_PORT
	global config
	
	# Setting up logging - add in time to it. Create a filename using time functions
	Now = datetime.datetime.now()
	LogFileName = 'log/pi-fighter_' + Now.strftime("%y%m%d%H%M") + ".log"

	# Sets up the logging - no special settings. 
	logging.basicConfig(filename=LogFileName,level=logging.DEBUG)

	# Setting up to read config file
	config = configparser.RawConfigParser()
	config.read('pi-fighter.cfg')

	#Get the sampling rate to use  
	SAMPLE_SLEEP = config.getint('TIMING', 'SAMPLE_SLEEP')

	# Get Display Sample - how often to update the display based on how many samples are taken before displaying
	DISPLAY_FREQ = config.getint('TIMING', 'DISPLAY_FREQ')

	# Get how long to typically wait between punches
	STD_PUNCH_WAIT = config.getint('TIMING', 'STD_PUNCH_WAIT')

	# Get how long to typically wait between punches
	CMD_FLASH_TIME = config.getint('TIMING', 'CMD_FLASH_TIME')
	BETWEEN_SEQ_REST = config.getint('TIMING', 'BETWEEN_SEQ_REST')

	# Get Server Information 

	SERVER_HOST= config['SERVER']['SERVER_HOST']
	UDP_PORT= int (config['SERVER']['UDP_PORT'])
	TCP_PORT= int (config['SERVER']['TCP_PORT'])
				

# Getting everything ready
InitialiseSystem() # initial setup
SetUpLoggingAndConfig() # Gather config info and start logging. 
