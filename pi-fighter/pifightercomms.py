import threading
import time
import queue 
from pifighterinit import *
import socket

def SendToServer(SendStr):
	try:
		# Open socket and send data - Open it each time as there were problems when comms wasn't great.
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as ServerSocket:
			# Connect to server and send data		
			ServerSocket.setblocking(False)					
			ServerSocket.sendto(bytes(SendStr, "utf-8"), (SERVER_HOST, SERVER_PORT))
	except:
		print ("Send Failure - who cares?  Not me.")


# Thread to handle outputting to the OLED screen and sending to the server. 
# - to avoid spending too much time blocked on this.
class ServerCommsThread (threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter

	def run(self):
		print ("Starting " + self.name)

		# Some initialisation
		LastDisplayTime = time.time()
		
		while (1):

			# Get the information from the Queue whenever available.  Pass it on to the server.  Not
			# too worried about losing a few attacks.  
			if (CommQueue.empty() == False):
				
				# Get each String
				QueueStr = CommQueue.get_nowait()
				
				#SkipCountInfo = "<Skip><SkipCount>{:d}</SkipCount></Skip>" .format(SkipCount)
				
				try:
					# Open socket and send data - Open it each time as there were problems when comms wasn't great.
					with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as ServerSocket:
						# Connect to server and send data		
						ServerSocket.setblocking(False)					
						ServerSocket.sendto(bytes(QueueStr, "utf-8"), (SERVER_HOST, SERVER_PORT))
				except:
					#raise
					print ("Send Failure - who cares?  Not me.")
					
		print ("Exiting " + self.name)
		exit()

ServerCommsThread = ServerCommsThread(1, "Attack Display Thread", 1) 
ServerCommsThread.start()

# Thread to handle the Server communications
class ServerCommsThread (threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
	def run(self):
		print ("Starting " + self.name)
		#print_time(self.name, self.counter, 5)
		
		print ("Exiting " + self.name)
