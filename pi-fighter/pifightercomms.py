import threading
import time
import queue 
import socket
import select

from pifighterinit import * 



'''
def UDPSendToServer(SendStr):
	try:
		# Open socket and send data - Open it each time as there were problems when comms wasn't great.
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as ServerSocket:
			# Connect to server and send data		
			ServerSocket.setblocking(False)					
			ServerSocket.sendto(bytes(SendStr, "utf-8"), (SERVER_HOST, UDP_PORT))
	except:
		print ("Send Failure - who cares?  Not me.")
'''

# Thread to handle UDP Comms. 
class UDPCommsThread (threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter

	def run(self):
		global SERVER_HOST
		global TCP_PORT

		#print ("Starting " + self.name)
		
		
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as UDPSocket:
			UDPSocket.setblocking(False)	

			while (1):
				
				try:				
					# Take anything that is in the Queue and send it on to the server. 
					if (UDPCommSendQueue.empty() == False):
						UDPStr = UDPCommSendQueue.get_nowait()
						UDPSocket.sendto(bytes(UDPStr, "utf-8"), (SERVER_HOST, UDP_PORT))
				
					# Connect to server and send data												
					InputSock,OutputSock, ExceptionSock = select.select([UDPSocket], [], [UDPSocket], 0.25)
						
					# Check for any responses 
					for CommSocket in InputSock:
						if CommSocket is UDPSocket:
							UDPRecStr = UDPSocket.recv(1024)
							#print (UDPRecStr)
							UDPCommRecQueue.put_nowait(UDPRecStr)
					
				except:
					print ("UDP Send Failure")
					raise

		'''
			if (UDPCommQueue.empty() == False):
				UDPStr = UDPCommQueue.get_nowait()
				
				try:
					UDPSendToServer (UDPStr)
					
					UDPSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
					
					InputSock,OutputSock, ExceptionSock = select.select([UDPSocket], [], [UDPSocket], 0.25)
					
					for CommSocket in InputSock:
						if CommSocket is UDPSocket:
							UDPRecStr = UDPSocket.recv(1024)
					
					
				except:
					print ("Send Failure - who cares?  Not me.")

			'''	

		print ("Exiting " + self.name)
		exit()

'''
# Thread to handle the Server communications
class UDPCommsThread (threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
	def run(self):
		print ("Starting " + self.name)
		#print_time(self.name, self.counter, 5)
		
		print ("Exiting " + self.name)
'''

# Thread to handle TCP Comms. 
class TCPCommsThread (threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter

	def run(self):
		global SERVER_HOST
		global TCP_PORT
		
		#print ("Starting " + self.name)
		
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPsocket:
			# Connect to server and send data
			TCPsocket.connect((SERVER_HOST, TCP_PORT))
		
			while (1):
				
				if (TCPCommSendQueue.empty() == False):
					TCPStr = TCPCommSendQueue.get_nowait()
					
					try:
						TCPsocket.sendall(bytes(  TCPStr + "\n", "utf-8"))
												
						# Wait a short period of time for anything on TCP Socket.  
						InputSock,OutputSock, ExceptionSock = select.select([TCPsocket], [], [TCPsocket], 0.25)
						
						# Go through sockets that got input
						for CommSocket in InputSock:
							if CommSocket is TCPsocket:
								TCPRecStr = TCPsocket.recv(1024)
								#print (TCPRecStr)
								TCPCommRecQueue.put_nowait(TCPRecStr)
						
					except:
						print ("TCP Send Failure")
						raise

				

'''
# Thread to handle the Server communications
class UDPCommsThread (threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
	def run(self):
		print ("Starting " + self.name)
		#print_time(self.name, self.counter, 5)
		
		print ("Exiting " + self.name)
'''

# Start the 2 threads to deal with the Comms - UDP for attacks, skips, etc.  TCP is used for managing session, etc.
# Both threads are set up a Daemon threads, so they will be killed when the main thread exits.
UDPCommsThread = UDPCommsThread(1, "UDP Data Transmission Thread - real time data might drop some packets.", 1) 
UDPCommsThread.setDaemon(True)
UDPCommsThread.start()
TCPCommsThread = TCPCommsThread(1, "TCP Data Transmission Thread - non real time data - manage session, etc.", 1) 
TCPCommsThread.setDaemon(True)
TCPCommsThread.start()
	
