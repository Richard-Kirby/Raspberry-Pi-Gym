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
import queue

# Brightness settings for showing accelerations
Brightness = [0,0,2,2,4,4,15,15]	


strip.InitStrip() # Get the Neopixel strip set up.  

# Max acceleration rate in the display period
MaxAccel = [0,0,0]
SampleNum = 0

Matrix.Setup()
Matrix.Intro()

#  If workout mode, then run through sequences of attacks. 
if (int(Mode) == WorkoutMode):
	# Setting up and starting the Attack thread.
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

elif (int(Mode) == KickButtMode):
	# Get list of Opponents
	SendToServer("<OpponentList></OpponentList>", "utf-8")
	time.sleep(3)
	ServerData = ServerSocket.recv(10*1024)
				
	# Decode to ASCII so it can be processed.
	ServerStr = ServerData.decode('ascii')
	
	print (ServerStr)
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
	
	SelectedOpponent = input("Select the number of the Opponent you would most like to spar with")
	
	print ("{} is your selected opponent - calling them to the ring" .format(OpponentList[int(SelectedOpponent)]))
	SelectedOppStr = "<SelectedOpponent>{}</SelectedOpponent>".format(OpponentList[int(SelectedOpponent)])
	print (SelectedOppStr)

	
	
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
		print (SampleNum, MaxAccel)

		MaxAccelInfo = "<Attack><Date>{}</Date><Time>{}</Time><XAccel>{:2.3}</XAccel><YAccel>{:2.3f}</YAccel><ZAccel>{:2.3f}</ZAccel></Attack>".format(date_string, time_string, MaxAccel[0], MaxAccel[1], MaxAccel[2])
		# print(MaxAccelInfo)
		#ServerSocket.sendall(bytes(MaxAccelInfo, "utf-8"))
		# Put the attack information into the queue for processing.  Only do this if the Z Accel > 1.5 - no 
		# processing otherwise.  The Queue sends it on to the server.  
		if (MaxAccel[2] > 1.5):
			CommQueue.put_nowait(MaxAccelInfo)
		
		# Draw pattern based on z accel (into chip) - scales 16g into 15 patterns by /2.1
		Matrix.DrawPattern(int(MaxAccel[2]/2.1), Brightness[int(MaxAccel[2]/2.1)])
		MaxAccel[0] = 0
		MaxAccel[1] = 0
		MaxAccel[2] = 0
		

	time.sleep(SAMPLE_SLEEP/1000)
	
	SampleNum +=1
	
	'''
	# Put the data into an XML Element Tree
	try:
		#print ("DEBUG")
		#ServerElement = ET.fromstring(ServerStr)
		# Check to see if there is anything from the server
		# self.request is the TCP socket connected to the client
		ServerData = ServerSocket.recv(10*1024)
				
		# Decode to ASCII so it can be processed.
		ServerStr = ServerData.decode('ascii')
	
		print (ServerStr)
		
		# Put the data into an XML Element Tree
		ServerElement = ET.fromstring(ServerStr)

		# Processing of Opponent Information
		if (ServerElement.tag == 'OpponentInfo'):
			for Child in ServerElement:	
				print (Child.tag + Child.text)
				if (Child.tag=='HealthPoints'):
					OpponentHealthPoints = float(Child.text)		
					IndicateHealthPoints(OpponentHealthPoints, 1)

		# Processing of an Attack from the opponent
		elif (ServerElement.tag == 'Attack'):
			for Child in ServerElement:

				# ZAccel does the damage - ignore if less than 2g
				if (Child.tag == 'ZAccel'):
					
					Damage = float(Child.text)
					if (Damage >2):
						UserHealthPoints = UserHealthPoints - Damage
						print (UserHealthPoints)
						IndicateHealthPoints (UserHealthPoints, 0)
						
						# Determine if Opponent is Defeated
						if (UserHealthPoints < 0):
							print ("Your opponent kicked your butt")
						

			
				print (Child.tag + Child.text)
				if (Child.tag=='HealthPoints'):
					OpponentHealthPoints = float(Child.text)		
					IndicateHealthPoints(OpponentHealthPoints, 1)
		else:
			print("Unable to process messsage from server: " + ServerStr)
					
	except BlockingIOError:
		0 # Do nothing - expecting blocking issues if nothing to receive
	except:
		print ("Unexpected Error")
		raise
	
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
