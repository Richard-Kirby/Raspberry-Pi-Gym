import socketserver
import socket
import xml.etree.ElementTree as ElementTree
import binascii
import configparser
import threading
import datetime
import logging
import time
import queue


#Set up the config parser
config = configparser.ConfigParser()

#Read the config file in.
config.read('pi-fighter-server.cfg')


while(1):
	for i in range(0,17,1):
		OpponentAttackStr = "<OpponentAttack>{}</OpponentAttack>".format(i)
		print(OpponentAttackStr)
		
		print(config['PI_TRAINER']['PI_TRAINER'], int(config['PI_TRAINER']['PI_TRAINER_PORT']))
		
		# Send the message via UDP to Pi Fighter
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as UDPSocket:
			UDPSocket.setblocking(False)

			UDPSocket.sendto(bytes(OpponentAttackStr, "utf-8"),(config['PI_TRAINER']['PI_TRAINER'], int(config['PI_TRAINER']['PI_TRAINER_PORT'])))
			UDPSocket.sendto(bytes(OpponentAttackStr, "utf-8"),("1.168.1.19", int(config['PI_TRAINER']['PI_TRAINER_PORT'])))

			time.sleep(1)
	
			


