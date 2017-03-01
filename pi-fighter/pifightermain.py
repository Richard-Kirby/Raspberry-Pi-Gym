#!/usr/bin/python3

import socket
import math
import time 
import pigpio # For managing any I/O 
import threading
import queue 
import xml.etree.ElementTree as ET

# pifighterinit does some of the initialisation for the program - getting mode set up, etc.   
from pifighterinit import *
import pifighterstrip as strip
import pifightercomms as comms
import pifightermatrix as Matrix
import pifighteraccel as Accel

# Brightness settings for showing accelerations
Brightness = [0,0,2,2,4,4,15,15]	


strip.InitStrip() # Get the Neopixel strip set up.  

# Max acceleration rate in the display period
MaxAccel = [0,0,0]
SampleNum = 0

Matrix.Setup()


def OpponentSetup():
	# Get list of Opponents
	
	TCPCommSendQueue.put_nowait("<OpponentList></OpponentList>")
	#print ("Put something into TCP Queue")
	
	#	Blocking waiting for a list of oppoonents. 
	ServerData = TCPCommRecQueue.get()

		
	# Decode to ASCII so it can be processed.
	ServerStr = ServerData.decode('ascii')
	
	#print (ServerStr)

	# Put the data into an XML Element Tree
	ServerElement = ET.fromstring(ServerStr)

	# Processing of Opponent Information - create a list of opponents
	OpponentList=[]
	
	if (ServerElement.tag == 'OpponentList'):
		for Child in ServerElement:	
			#print (Child.tag + Child.text)
			if (Child.tag=='Opponent'):
				OpponentInfo = Child.text	
				OpponentList.append(OpponentInfo)

	i = 0 
	for Opponent in OpponentList:
		print ("{:d}. {}" .format(i,Opponent))
		i += 1
	
	SelectedOpponent = input("Select the number of the Opponent:")
	
	print ("{} is your selected opponent - calling them to the ring" .format(OpponentList[int(SelectedOpponent)]))
	SelectedOppStr = "<SelectedOpponent>{}</SelectedOpponent>".format(OpponentList[int(SelectedOpponent)])
	TCPCommSendQueue.put_nowait(SelectedOppStr)
	UDPCommSendQueue.put_nowait(SelectedOppStr)
	
	
	# Waiting to hear back from the server - will indicate the opponent is ready.  
	ServerData = TCPCommRecQueue.get()

	# Decode to ASCII so it can be processed.
	ServerStr = ServerData.decode('ascii')
	
	# Put the data into an XML Element Tree
	ServerElement = ET.fromstring(ServerStr)

	if (ServerElement.tag == 'OpponentReady'):
		Opponent = ServerElement.text
		
		print ("{} is ready to take you apart - are you scared?  You should be! ".format (Opponent))

		Matrix.Intro("Pi-Fighting {}" .format(Opponent))
	
	else:
		print ("Trouble processing String {}", ServerElement.tag)

	return Opponent


#  If workout mode, then run through sequences of attacks. 
if (int(Mode) == WorkoutMode):
	# Setting up and starting the Attack thread.
	Matrix.Intro("Pi-Fighter - workout")
	
	print ("Setting Up Attack Seq")
	PunchThread = strip.AttackSeqThread(1, "Attack Thread", 1) 
	PunchThread.start()
	
	# Connect to server and send data
	
	#data = "<User>pi-fighter User is {} </User>" .format(UserName)	
	# Send data to the server
	#ServerSocket.sendall(bytes(  data + "\n", "utf-8"))

	# Receive data from the server and shut down
	#received = str(sock.recv(1024), "utf-8")
		
	#print("Sent:     {}".format(data))
	#print("Received: {}".format(received))

# If User wants a fight, then set up the opponent. 
elif (int(Mode) == KickButtMode):
	Opponent = OpponentSetup()

else:
	print("Mode Processing Error {}", Mode)
	
	
# Function to deal with strings that are sent by the server.  Things like opponent information, opponent attacks. 

def ProcessServerStr(UDPqData):

	global VictoryDeclared

	try:
		# Decode to ASCII so it can be processed.
		ServerStr = UDPqData.decode('ascii')
	
	
		# Put the data into an XML Element Tree
		ServerElement = ET.fromstring(UDPqData)

		# Processing of Opponent Information
		if (ServerElement.tag == 'OpponentInfo'):
			for Child in ServerElement:	
				
				# Process the Opponent String information
				if (Child.tag=='Name'):
					OpponentName = Child.text
				
				# Indicate the health points on the 2nd strip. 
				elif (Child.tag=='HealthPoints'):
					OpponentHealthPoints = float(Child.text)		
					strip.IndicateHealthPoints(OpponentHealthPoints, 1)
				
				# If the opponent is defeated display victory string.  
				elif (Child.tag=='Defeated'):
					print ("Defeated Flag {}".format(Child.text))
					if (Child.text == 'False'):
						VictoryDeclared = False
					elif (Child.text == 'True' and VictoryDeclared == False):
						VictoryDeclared = True
						VictoryStr = ("You defeated {}!! Shocker" .format(OpponentName))
						Matrix.DisplayStr(VictoryStr)	
						time.sleep(5)
						Matrix.DisplayStr("...................Fight Another?")
						Opponent = OpponentSetup()	
						
						# Clearing out the Queue of any junk, so there is no confusion 
						# between this fight and the last one.  
						while not UDPCommRecQueue.empty():
							UDPCommRecQueue.get_nowait()
						
						

		# Processing of an Attack from the opponent
		elif (ServerElement.tag == 'PlayerInfo'):
			for Child in ServerElement:

				# Get HealthPoints
				if (Child.tag == 'Defeated'):
					
					# Determine if Opponent is Defeated
					if (Child.text == 'True'):
							print ("Your opponent kicked your butt")
						

				
				if (Child.tag=='HealthPoints'):
					print ("Process Health")
					PlayerHealthPoints = float(Child.text)		
					strip.IndicateHealthPoints(PlayerHealthPoints, 0)
		
		
		else:
			print("Unable to process messsage from server: " + ServerStr)
	except:
		print ("Unexpected Error")
		raise		

			
	
	

	
	
while(1):
		
	# Grab Accelerometer Data 
	ScaledAccel = Accel.GetScaledAccelValues() # X,Y,Z acceleration
	#print (ScaledAccel)
	date_string = datetime.datetime.now().date()
	time_string = datetime.datetime.now().time()
	
	AttackInfo = "<Attack><Date>{}</Date><Time>{}</Time><XAccel>{:2.3}</XAccel><YAccel>{:2.3f}</YAccel><ZAccel>{:2.3f}</ZAccel></Attack>" .format(date_string, time_string, ScaledAccel[0], ScaledAccel[1], ScaledAccel[2])
	
	logging.info(AttackInfo)
	
	# Update Max Accel if needed - loop through XYZ acceleration
	for i in range(3):
		# Sorting out maximmum acceleration for this period
		if (abs(ScaledAccel[i]) > MaxAccel[i]):
			MaxAccel[i] = abs(ScaledAccel[i])
	
	# Check to see if this cycle is one in which we need to report the max accel - configurable. 
	if (SampleNum % DISPLAY_FREQ == 0):

		# Create the string to send to the server. 
		MaxAccelInfo = "<Attack><Date>{}</Date><Time>{}</Time><User>{}</User><XAccel>{:2.3}</XAccel><YAccel>{:2.3f}</YAccel><ZAccel>{:2.3f}</ZAccel></Attack>".format(date_string, time_string, UserName, MaxAccel[0], MaxAccel[1], MaxAccel[2])
		
		# Put the attack information into the queue for processing.  Only do this if the Z Accel > 1.5 - no 
		# processing otherwise.  The Queue sends it on to the server.  
		if (MaxAccel[2] > 1.5):
			print ("Decent Hit of {:02.2f}" .format(MaxAccel[2]))
			UDPCommSendQueue.put_nowait(MaxAccelInfo)
		
		# Draw pattern based on z accel (into chip) - scales 16g into 15 patterns by /2.1
		Matrix.DrawPattern(int(MaxAccel[2]/2.1), Brightness[int(MaxAccel[2]/2.1)])
		MaxAccel[0] = 0
		MaxAccel[1] = 0
		MaxAccel[2] = 0
		
	if (UDPCommRecQueue.empty() == False):
		UDPqData = UDPCommRecQueue.get_nowait()
		ProcessServerStr(UDPqData)
	
			
	time.sleep(SAMPLE_SLEEP/1000)
	
	SampleNum +=1
	

		
'''
	# Put the data into an XML Element Tree
	
	# If Opponent Information Received.
	if (ClientElement.tag == 'Attack'):

		# Read through all the information
		for Child in ClientElement:
			#print (Child.tag)
			
			# ZAccel does the damage - ignore if less than 2g
			if (Child.tag == 'ZAccel'):
				#print(Child.text)
				
				Damage = float(Child.text)
				if (Damage >2):
					HealthPoints = HealthPoints - Damage
					print (HealthPoints)
					
					# Determine if Opponent is Defeated
					if (HitPoints < 0):
						if (OppoonentDefeated == FALSE):
							print ("That dude is finished")
							OpponentDefeated = True
					
					# Send Opponent Information to the Client for display or other usage.
					SendOpponentInfo()
	'''
	
	
'''
	except KeyboardInterrupt: 
		print ("Fine - quit see if I care - jerk")
		exit()
	except:
		#rint("Unexpected error:", sys.exc_info()[0])
		raise
'''	
