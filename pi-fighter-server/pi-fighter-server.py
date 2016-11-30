import socketserver
import socket
import xml.etree.ElementTree as ElementTree
import binascii

Opponents = {"One ewok": 50,"C3-PO": 60, "Early Luke SkyWalker":80, "R2D2": 100, "Jedi Luke": 200, "Yoda": 200, "Many Ewoks": 200, "JarJar Binks":70}

HealthPoints = 100
NumAttacks = 0 
OpponentDefeated = False
FinalAttackNum = 0

class PiFighterHandler(socketserver.BaseRequestHandler):


	"""
	The request handler class for our server.

	It is instantiated once per connection to the server, and must
	override the handle() method to implement communication to the
	client.
	
	"""

	def SendOpponentInfo(self):
		global HealthPoints
		global NumAttacks
		global OpponentDefeated
		OpponentHealthStr = "<OpponentInfo><Name>{}</Name><Defeated>{}</Defeated><HealthPoints>{}</HealthPoints></OpponentInfo>".format("Daffy", OpponentDefeated, HealthPoints)		
		#self.request.sendall(bytes(OpponentHealthStr,"utf-8" ))
		socket = self.request[1]
		socket.sendto(bytes("got it", "utf-8"), self.client_address)

	def SendAttack(self, date_string, time_string, MaxAccel):
		AttackStr = "<Attack><Date>{}</Date><Time>{}</Time><XAccel>{:2.3}</XAccel><YAccel>{:2.3f}</YAccel><ZAccel>{:2.3f}</ZAccel></Attack>".format(date_string, time_string, MaxAccel[0], MaxAccel[1], MaxAccel[2])
		self.request.sendall(bytes(AttackStr,"utf-8" ))
	
		
	def handle(self):
		global HealthPoints
		global NumAttacks
		global OpponentDefeated
		global FinalAttackNum
		
		self.timeout = 0 
		#self.SendOpponentInfo()
		
		#while (1):
		# self.request is the TCP socket connected to the client
		self.data = self.request[0].strip()
		socket = self.request[1]
		
		# to send data .... 
		socket.sendto(bytes("got it", "utf-8"), self.client_address)

		
		# Decode to ASCII so it can be processed.
		ClientStr = self.data.decode('ascii')
		
		# Put the data into an XML Element Tree
		try:
			print (ClientStr)
			ClientElement = ElementTree.fromstring(ClientStr)
			# If Attack received, then calcualte the effect on the opponent.
		
			if (ClientElement.tag == 'Attack'):

			
				# Read through all the information
				for Child in ClientElement:
					#print (Child.tag)
					
					# ZAccel does the damage - ignore if less than 2g
					if (Child.tag == 'ZAccel'):
						print(Child.text)
						Damage = float(Child.text)

						
						if (Damage >2):
							HealthPoints -= Damage
							NumAttacks += 1
							print (NumAttacks, HealthPoints)
							
							# Determine if Opponent is Defeated
							if (HealthPoints < 0):
								if (OpponentDefeated == False):
									FinalAttackNum = NumAttacks
									OpponentDefeated = True
								if (OpponentDefeated == True):
									print ("That dude is finished after - stop beating on him/her - Oh the Humanity", FinalAttackNum)

							
							# Send Opponent Information to the Client for display or other usage.
							self.SendOpponentInfo()
			elif (ClientElement.tag == 'OpponentList'):
				OpponentStr = "<OpponentList>"
				for Opponent in Opponents:
					Name = Opponent
					HealthPoints = Opponents[Opponent]
					OpponentStr += "<Opponent>{}</Opponent>" .format(Name)
				
				OpponentStr += "</OpponentList>"
				print (OpponentStr)
				self.request.sendall(bytes(OpponentStr,"utf-8" ))
				
			elif (ClientElement.tag == 'Skip'):
				for Child in ClientElement:
					if (Child.tag == 'SkipCount'):
						print (Child.tag, Child.text)
		except:
			print ("Trouble Processing String: {}" .format(ClientStr))
			raise()
			
							
'''	
	for Sequence in Seq_root:
		
		print (Sequence.attrib)
		#device.show_message(Sequence.attrib, font=proportional(CP437_FONT), delay = 0.05)
		#time.sleep(.4)


		for Command in Sequence:
			PixelState = [NO_STATE_COLOUR, NO_STATE_COLOUR, NO_STATE_COLOUR, NO_STATE_COLOUR, 
			                NO_STATE_COLOUR, NO_STATE_COLOUR, NO_STATE_COLOUR, NO_STATE_COLOUR,
							NO_STATE_COLOUR, NO_STATE_COLOUR, NO_STATE_COLOUR, NO_STATE_COLOUR, 
			                NO_STATE_COLOUR, NO_STATE_COLOUR, NO_STATE_COLOUR, NO_STATE_COLOUR]
							
			print (Command.tag)
			if Command.tag == 'Attack':
				for Attack in Command:
					print (Attack.tag)
					#print (Attack.text)
'''
			

if __name__ == "__main__":
	IP = socket.gethostbyname_ex("KirbyDell")
	print (IP)
	HOST, PORT = "KirbyDell", 9999
	# Create the server, binding to localhost on port 9999
	server = socketserver.UDPServer((HOST, PORT), PiFighterHandler)

	# Activate the server; this will keep running until you
	# interrupt the program with Ctrl-C
	server.serve_forever()
	
	
	
	