#!/usr/bin/python3

import socket
import socketserver
import smbus  # need to get smbus library by the following command $sudo apt-get install python-smbus
import math
import time 
import pigpio # For managing any I/O 
import datetime
import logging 
import configparser

import threading
import xml.etree.ElementTree as ElementTree
import queue


import signal

import scrollphathd
from scrollphathd.fonts import font5x7

print("""
Scroll pHAT HD: Hello World

Scrolls "Hello World" across the screen
in a 5x7 pixel large font.

Press Ctrl+C to exit!

""")

# This bit just gets the pigpiod daemon up and running if it isn't already.  
import subprocess
import os 

p = subprocess.Popen(['pgrep', '-f', 'pigpiod'], stdout=subprocess.PIPE)
out, err = p.communicate()

if len(out.strip()) == 0:
    os.system("sudo pigpiod")
# End of getting pigpiod running. 
	

# Set up the Pigpiod Pi.  
pi = pigpio.pi()


# GPIO Definitions for the vibrators (3 count)
Vibrators = [17, 27, 22]


# Setting up logging - add in time to it. Create a filename using time functions
Now = datetime.datetime.now()
LogFileName = "PiTrainer_" + Now.strftime("%y%m%H%M") + ".log"

# Sets up the logging - no special settings. 
logging.basicConfig(filename=LogFileName,level=logging.DEBUG)

# Setting up to read config file
config = configparser.RawConfigParser()
config.read('PiTrainer.cfg')


#Get the sampling rate to use  
SAMPLE_SLEEP = config.getint('TIMING', 'SAMPLE_SLEEP')

# Get Display Sample - how often to update the display based on how many samples are taken before displaying
DISPLAY_FREQ = config.getint('TIMING', 'DISPLAY_FREQ')

# Get Skip Threshold - the g force that has to be exceeded to register one skip count.  
SKIP_THRESHOLD = config.getint('THRESHOLDS', 'SKIP_THRESHOLD')
	
# Get Server Information 
SERVER_HOST= config['SERVER']['SERVER_HOST']
SERVER_PORT= int (config['SERVER']['SERVER_PORT'])


# Power management registers for accelerometer
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

# Standard reading functions for Accelerometer
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

# Max acceleration rate in the display period
MaxAccel = 0
SampleNum = 0
SkipCount = 0 

# Creat a queue for talking between the threads
q = queue.Queue()

# Queue to send Rumble Requests.  
RumbleQ = queue.Queue()

# Thread to handle outputting to the OLED screen and sending to the server. 
# - to avoid spending too much time blocked on this.
class CountDisplayThread (threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
	def run(self):
		print ("Starting " + self.name)
		#print_time(self.name, self.counter, 5)
		
		# Some initialisation
		LastDisplayTime = time.time()
		SkipCount = 0 

		print (SERVER_HOST, SERVER_PORT)

		while (1):
			# Print to the OLED Screen - Get the information from the Queue whenever available, but only update OLED screen once in a while
			# Screen is too slow for many updates. 
			if (q.empty() == False):
				SkipCount = q.get_nowait()
				
				SkipCountInfo = "<Skip><SkipCount>{:d}</SkipCount></Skip>" .format(SkipCount)
				
				try:
					# Open socket and send data - Open it each time as there were problems when comms wasn't great.
					with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as ServerSocket:
						# Connect to server and send data		
						ServerSocket.setblocking(False)					
						ServerSocket.sendto(bytes(SkipCountInfo, "utf-8"), (SERVER_HOST, SERVER_PORT))
				except:
					print ("Send Failure - who cares?  Not me.")

			
			SkipCountStr = "{:d}".format(SkipCount)
			ElapsedTime = time.time() - LastDisplayTime
			
			if (ElapsedTime > 2):
				scrollphathd.clear()
				scrollphathd.write_string(SkipCountStr, x=0, y=0, font=font5x7, brightness=0.5)
				scrollphathd.show()
				LastDisplayTime = time.time()
				

		print ("Exiting " + self.name)
		exit()

SkipCountDisplayThread = CountDisplayThread(1, "Count Display Thread", 1) 
SkipCountDisplayThread.start()


'''

# Thread to handle messages from the Server.  
class ServerMessageThread (threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
	def run(self):
		print ("Starting " + self.name)
		#print_time(self.name, self.counter, 5)
		

		print (SERVER_HOST, SERVER_PORT)

		
		while (1):
		
			
			try:
				
				# Open socket and send data - Open it each time as there were problems when comms wasn't great.
				with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as ServerSocket:

					# Connect to server and send data		
					ServerSocket.setblocking(False)					
					ServerSocket.sendto(bytes(SkipCountInfo, "utf-8"), (SERVER_HOST, SERVER_PORT))
				
			except:
				print ("Send Failure - who cares?  Not me.")
			

		print ("Exiting " + self.name)
		exit()

ServerMsgThread = ServerMessageThread(1, "Server Message Thread", 1) 
ServerMsgThread.start()
'''



class UDPRecHandler(socketserver.BaseRequestHandler):
	
	
	"""
	The request handler class for our server.

	It is instantianted once per connection to the server, and must
	override the handle() method to implement communication to the
	client.
	
	"""

	def handle(self):
	
		print("handler")
		
		# self.request is the UDP socket connected to the client
		self.data = self.request[0].strip()
		socket = self.request[1]
		
	
		# Decode to ASCII so it can be processed.
		ClientStr = self.data.decode('ascii')
		
		# Put the data into an XML Element Tree
		try:
			print (ClientStr)
			ClientElement = ElementTree.fromstring(ClientStr)
	
			
			# If Attack received, then calcualte the effect on the opponent.
			
			if (ClientElement.tag == 'OpponentAttack'):

				print(ClientElement.text)
				
				PercentVibe = float(float(ClientElement.text)/16.0 *100) 
				print(PercentVibe)
				
				RumbleStr = "<Rumble><Vib0Str>{}</Vib0Str><Vib1Str>{}</Vib1Str><Vib2Str>{}</Vib2Str><MsDuration>{}</MsDuration></Rumble>" .format(int(PercentVibe), int(PercentVibe), int(PercentVibe), int(2 * PercentVibe))
				
				RumbleQ.put_nowait(RumbleStr)
				
				'''	
				# Read through all the information
				for Child in ClientElement:
					#print (Child.tag)
					
					# ZAccel does the damage - ignore if less than 2g
					if (Child.tag == 'ZAccel'):
						#print(Child.text)
						Damage = float(Child.text)

						
						if (Damage >2):
							Opponent.DecrementHealth(Damage)
							NumAttacks += 1
							#print (NumAttacks, HealthPoints)

							# Determine if Opponent is Defeated
							if (Opponent.CurrentHealth < 0):
								if (OpponentDefeated == False):
									FinalAttackNum = NumAttacks
									OpponentDefeated = True
									FightOver.set()
									
									# Player won, allow up to 50% regen
									Player.Regen(50)
									
									# Reward player with 2% of the opponents health points
									Player.RewardHealthPoint(0.02*Opponent.InitialHealth)
								
									# Keep Player Information up to date in XML as well. 
									PlayerMgr.UpdatePlayerXML(Player)
									PlayerMgr.UpdatePlayerFile()
	

									
								if (OpponentDefeated == True):
									print ("That dude is finished after - stop beating on him/her - Oh the Humanity", FinalAttackNum)

							
							# Send Opponent Information to the Client for display or other usage.
							self.SendOpponentInfo()
						
							# If first attack (player gets first punch), then start up the attacks from the opponent. 
							if (NumAttacks == 1):
								print ("run attacker thread")
								# Spin off opponent thread here.  
								AttackerThread = OpponentAttackThread(1, "Attacker Thread - Punch Up", 1, Opponent) 
								#AttackerThread.setDaemon(True)
								AttackerThread.start()
								FirstAttack = False
				'''
			else:
				print("Can't process string {}".format(ClientStr))
				
		except:
			print ("Trouble Processing String: {}" .format(ClientStr))
			raise()
			


# Class to handle the UDP Comms - manages the attacks and other messages from the Pi Fighter App, etc. 
class UDPRecThread (threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter

	def run(self):
		print ("Starting " + self.name)
		
		try:
			#print ("UDP")
			hostname = socket.gethostbyname("KirbyPiZeroW")
			#hostname = "localhost"
			print(socket.getfqdn())
			print ("UDP - Trying again", hostname, int(config['UDP']['PI_TRAINER_PORT']))
			
			# Create the UDP server.  
			UDPserver = socketserver.UDPServer((hostname, int(config['UDP']['PI_TRAINER_PORT'])), UDPRecHandler)
	
			# Activate the server; this will keep running until you
			# interrupt the program with Ctrl-C
			UDPserver.serve_forever()
			
		except:
			print("UDP Exception")
			raise

			
		finally:
			UDPServer.close()
			exit()

# Start up the Rumble Thread.  
UDPRecThreadHdl = UDPRecThread(1, "UDP Rec Thread", 1) 
UDPRecThreadHdl.start()




# Thread to handle Rumbling on command.
class RumbleThread (threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
	
		
	def run(self):
		print ("Starting " + self.name)
		#print_time(self.name, self.counter, 5)
		
		# Some initialisation
		# LastDisplayTime = time.time()

		# print (SERVER_HOST, SERVER_PORT)

		while(1):
			# Do the Rumble as required by the Queue 
			if (RumbleQ.empty() == False):
				RumbleStr = RumbleQ.get_nowait()
				
				# Accept XML string that specifies rumble information 
				# <Rumble><Vib0Str>0-100</Vib0Str><Vib1Str>0-100</Vib1Str><Vib2Str>0-100</Vib2Str><MsDuration>0-10000</MsDuration></Rumble>  

				print (RumbleStr)
				RumbleElement = ElementTree.fromstring(RumbleStr)
		
				# If Rumble - process it. 
				VibeStr =[0,0,0]
				
				if (RumbleElement.tag == 'Rumble'):
					
					# Read through all the information
					for Child in RumbleElement:
						
						# Get Vib Array Strengths
						if (Child.tag == 'Vib0Str'):
							#print(Child.text)
							VibeStr[0] = int(Child.text)
							
						# Get Vib Array Strengths
						if (Child.tag == 'Vib1Str'):
							#print(Child.text)
							VibeStr[1] = int(Child.text)
							
						# Get Vib Array Strengths
						if (Child.tag == 'Vib2Str'):
							#print(Child.text)
							VibeStr[2] = int(Child.text)

						# Get the duration to rumble. 
						if (Child.tag == 'MsDuration'):
							#print(Child.text)
							msduration = int(Child.text)

					# Run the requested Vibrations
					
					for i in range(0,3):
						PWM = int(int(VibeStr[i])*255/100)
						if (PWM > 255):
							PWM =255 
							
						#print ("***", PWM)
						pi.set_PWM_dutycycle(Vibrators[i], PWM)
						
						#pi.set_PWM_dutycycle(Vibrators[i], 100)
					
					time.sleep(float(msduration/1000))
					#time.sleep(.05)
					for i in range(0,3):
						pi.set_PWM_dutycycle(Vibrators[i], 0)
					time.sleep(.3)
					
		print ("Exiting " + self.name)
		exit()

# Start up the Rumble Thread.  
RumbleThreadHdl = RumbleThread(1, "Rumble Thread", 1) 
RumbleThreadHdl.start()


#with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as ServerSocket:
	
# Connect to server and send data
#ServerSocket.setblocking(False)
#data = "<User>pi-fighter User is {} </User>" .format(UserName)	
# Send data to the server
#ServerSocket.sendall(bytes(  data + "\n", "utf-8"))

# Receive data from the server and shut down
#received = str(sock.recv(1024), "utf-8")
	
#print("Sent:     {}".format(data))
#print("Received: {}".format(received))

# Short test to confirm each of the vibrators is working.
for i in range(0,3):
	print ("Vibrator ", i)

	VibrStrength= [0,0,0]
	for j in range(20,100,20):
		VibrStrength[i]=j
		RumbleCmd = str("<Rumble><Vib0Str>{}</Vib0Str><Vib1Str>{}</Vib1Str><Vib2Str>{}</Vib2Str><MsDuration>200</MsDuration></Rumble>".format(VibrStrength[0],VibrStrength[1],VibrStrength[2]))
		RumbleQ.put_nowait(RumbleCmd)
		time.sleep(0.5)
	time.sleep(1)


while(1):
	try:
		
		# Grab Accelerometer Data 
		ScaledAccel = GetScaledAccelValues() # X,Y,Z acceleration
		#print (ScaledAccel)
		date_string = datetime.datetime.now().date()
		time_string= datetime.datetime.now().time()

		TotalAccel = math.sqrt(ScaledAccel[0] **2 + ScaledAccel[1] **2 + ScaledAccel[2] **2 )
				
		# Set the sign of the acceleration by a simple sum of the components
		if ((ScaledAccel[0] + ScaledAccel[1] + ScaledAccel[2]) <0):
			TotalAccel = -1 * TotalAccel
		
		#print ("{},{},{:2.3},{:2.3f}, {:2.3f}" .format(date_string, time_string, ScaledAccel[0], ScaledAccel[1], ScaledAccel[2]))
		logging.info("{},{},{:2.3},{:2.3f}, {:2.3f}, {:2.3f}" .format(date_string, time_string, ScaledAccel[0], ScaledAccel[1], ScaledAccel[2], TotalAccel))
		
				
		# Update Accel if needed
		if (abs(TotalAccel) > MaxAccel):
			MaxAccel = abs(TotalAccel)
		
		# If Skip is detected due to the threshold being exceeded, then update the skip count
		# and put it into the queue for processing by the OLED thread.  OLED thread is too slow to 
		# keep up with the skipping and print to the OLED which has a low refresh rate.  
		if (SampleNum % DISPLAY_FREQ == 0):
			#print ("Max :", MaxAccel)
			if (MaxAccel > SKIP_THRESHOLD):
				SkipCount = SkipCount + 1 
				print (SkipCount)
				
				# Put into the queue for processing.  
				q.put_nowait(SkipCount)
				#OLED_Print(SkipCountStr,"Verdana.ttf", 20, disp.width, disp.height)
				#SkipCountInfo = "<Skip><Date>{}</Date><Time>{}</Time><SkipCount>{:d}</SkipCount></Skip>" .format(date_string, time_string, SkipCount)
				
				# Sending skip count to the server. 
				#if (ServerSocket != 0):
				#	ServerSocket.sendto(bytes(SkipCountInfo, "utf-8"), (SERVER_HOST, SERVER_PORT))
				#else:
				#	print ("No Server Socket")
			#DrawPattern(int(MaxAccel/2.1), Brightness[int(MaxAccel/2.1)])
			MaxAccel = 0
	
		time.sleep(SAMPLE_SLEEP/1000)
		SampleNum +=1
	
	except KeyboardInterrupt: 
		print ("Fine - quit see if I care - jerk")
		
		# Asks the thread to finish nicely.
		SkipCountDisplayThread.join()

		exit()
		
