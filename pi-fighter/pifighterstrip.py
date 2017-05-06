import neopixel
import threading
import xml.etree.ElementTree as ET
import time
from pifighterinit import *

# Setting up the various colours
LEFT_PUNCH_COLOUR = neopixel.Color(255,0,0)
RIGHT_PUNCH_COLOUR = neopixel.Color(0,255,0)
LEFT_KICK_COLOUR = neopixel.Color(255,0,50)
RIGHT_KICK_COLOUR = neopixel.Color(0,255,100)
WAIT_COLOUR = neopixel.Color(0,0,255)
NO_STATE_COLOUR = neopixel.Color(0,0,0)
FINISHED_COLOUR = neopixel.Color(255,255, 255)

# KickButt Mode Colours
VERY_HEALTHY_COLOUR = neopixel.Color(0,100,0) # RGB
DAMAGED_COLOUR = neopixel.Color(100,100,0)
DANGER_COLOUR = neopixel.Color(100,0,0)
KO_COLOUR = neopixel.Color(0,0,100)

# WS2812 - LED strip configuration:
LED_COUNT      = 16      # Number of LED pixels. 0-7 on right 8-15 on left.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255      # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

def InitStrip():
	global strip 
	
	# Create NeoPixel object with appropriate configuration.
	strip = neopixel.Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)

	# Intialize the library (must be called once before other functions).
	strip.begin()

# Thread to handle the Attack sequences
class AttackSeqThread (threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
	def run(self):
		print ("Starting " + self.name)
		#print_time(self.name, self.counter, 5)
		RunPunchSequence()
		print ("Exiting " + self.name)


		
# Runs the Punch Sequence - expected go be run as a separate thread, so it can happen in parallell. 
def RunPunchSequence():
	global strip 
	global STD_PUNCH_WAIT
	global CMD_FLASH_TIME
	global BETWEEN_SEQ_REST
	
	# Read in the sequences from the XML file.
	SequenceTree = ET.parse('pi-fighter_seq.xml')
	Seq_root = SequenceTree.getroot()
	#print (Seq_root.tag)
	
	# Start from last pixel in the strip. 
	CurrentPixel = strip.numPixels() - 1
	
	for Sequence in Seq_root:
		
		print (Sequence.attrib)
		#device.show_message(Sequence.attrib, font=proportional(CP437_FONT), delay = 0.05)
		#time.sleep(.4)


		for Command in Sequence:
			PixelState = [NO_STATE_COLOUR, NO_STATE_COLOUR, NO_STATE_COLOUR, NO_STATE_COLOUR, 
			                NO_STATE_COLOUR, NO_STATE_COLOUR, NO_STATE_COLOUR, NO_STATE_COLOUR,
							NO_STATE_COLOUR, NO_STATE_COLOUR, NO_STATE_COLOUR, NO_STATE_COLOUR, 
			                NO_STATE_COLOUR, NO_STATE_COLOUR, NO_STATE_COLOUR, NO_STATE_COLOUR]
							
			#print (Command.tag)
			if Command.tag == 'Attack':
				for Attack in Command:
					#print (Attack.tag)
					#print (Attack.text)
				
					if Attack.tag == 'Punch':					
						#print(Attack.text)
						# Set the colour according to left or right
						if Attack.text == 'Left' : 
							AttackColour = LEFT_PUNCH_COLOUR
							for i in range (12,16):
								PixelState[i] = AttackColour
						elif Attack.text == 'Right' :
							for i in range (0,4):
								AttackColour = RIGHT_PUNCH_COLOUR
								PixelState[i] = AttackColour
						else:
							AttackColour =0
							print ("Unrecognised text", Attack.text)
					
						if AttackColour != 0:
						
							for i in range (0,16):
								
								# Set the current pixel as required by the punch sequence - use half the time to display, 
								# half off so it is sequence can have 2 of the same in a row
								strip.setPixelColor(i, PixelState[i]) # Actual strip is Green Red Blue, so swap colours around
							strip.show()
							time.sleep(CMD_FLASH_TIME/1000)

							for i in range (0,16):
								
								# Set the current pixel as required by the punch sequence - use half the time to display, 
								# half off so it is sequence can have 2 of the same in a row
								strip.setPixelColor(i, neopixel.Color(0,0,0)) # Actual strip is Green Red Blue, so swap colours around

							strip.show()
						
							
					if Attack.tag == 'Kick':					
						#print(Attack.text)
						# Set the colour according to left or right
						if Attack.text == 'Left' : 
							AttackColour = LEFT_KICK_COLOUR
							for i in range (8,12):
								PixelState[i] = AttackColour
						elif Attack.text == 'Right' :
							for i in range (4,8):
								AttackColour = RIGHT_KICK_COLOUR
								PixelState[i] = AttackColour
						else:
							AttackColour =0
							print ("Unrecognised text", Attack.text)
					
						if AttackColour != 0:
						
							for i in range (0,16):
								
								# Set the current pixel as required by the punch sequence - use half the time to display, 
								# half off so it is sequence can have 2 of the same in a row
								strip.setPixelColor(i, PixelState[i]) # Actual strip is Green Red Blue, so swap colours around
							strip.show()
							time.sleep(CMD_FLASH_TIME/1000)

							for i in range (0,16):
								
								# Set the current pixel as required by the punch sequence - use half the time to display, 
								# half off so it is sequence can have 2 of the same in a row
								strip.setPixelColor(i, neopixel.Color(0,0,0)) # Actual strip is Green Red Blue, so swap colours around

							strip.show()
						
							
					elif Attack.tag == 'Wait':
						#print(Attack.text)
						for i in range (0,16):
							AttackColour = NO_STATE_COLOUR
							PixelState[i] = AttackColour
							strip.setPixelColor(i, PixelState[i])
						strip.show()
						AttackWait = (int) (Attack.text) * STD_PUNCH_WAIT / 1000
	
						time.sleep(AttackWait)
			elif Command.tag == 'Rest':
				#print (Command.text)
				CommandWait = (int) (Command.text) * STD_PUNCH_WAIT / 1000
				strip.setPixelColor(CurrentPixel, WAIT_COLOUR) # Turn pixel white when finished
				strip.show()
				time.sleep(CommandWait)
				

			
		strip.setPixelColor(CurrentPixel, FINISHED_COLOUR) # Turn pixel white when finished
		CurrentPixel -= 1
		strip.show()
		time.sleep(BETWEEN_SEQ_REST/1000)
		
		# flash to tell the person to get ready
		strip.setPixelColor(CurrentPixel, WAIT_COLOUR) # Turn pixel white when finished
		strip.show()
		time.sleep(3)
		strip.setPixelColor(CurrentPixel, neopixel.Color(0,0,0)) # Turn pixel off when finished
		strip.show()
		time.sleep(3)

def IndicateHealthPoints(HealthPoints, Strip):
	global strip 
	
	HealthPixels = round(HealthPoints/25)
	
	if (HealthPoints >0 and HealthPixels == 0):
		HealthPixels = 1
	
	print (HealthPoints)
	if (HealthPoints > 85):
		PixelColour = VERY_HEALTHY_COLOUR
	elif (HealthPoints >=60 and HealthPoints <=85):
		PixelColour = DAMAGED_COLOUR	
	elif (HealthPoints >=0 and HealthPoints <60):
		PixelColour = DANGER_COLOUR
	elif (HealthPoints<0):
		PixelColour = KO_COLOUR
		
	if (Strip ==0):
		if (PixelColour == KO_COLOUR):
			for i in range (7, -1 ,-1):
				strip.setPixelColor(i, neopixel.Color(0,0,0)) 
			strip.show()
			time.sleep(.3)
			for i in range (7, -1 ,-1):
				strip.setPixelColor(i, PixelColour) # Indicate Knock Out
			
		# Otherwise indicate health
		else:
		
			# Otherwise indicate health
			for i in range (7, 7 - HealthPixels ,-1):
				strip.setPixelColor(i, PixelColour) 
			for i in range (7-HealthPixels,-1 ,-1):
				strip.setPixelColor(i, neopixel.Color(0,0,0)) 

	elif (Strip ==1):
		if (PixelColour == KO_COLOUR):
			for i in range (8, 16):
				strip.setPixelColor(i, neopixel.Color(0,0,0)) # Indicate Knock Out
			strip.show()
			time.sleep(.3)
			for i in range (8, 16):
				strip.setPixelColor(i, PixelColour) # Indicate Knock Out
		else:	
			for i in range (8, 8 + HealthPixels):
				strip.setPixelColor(i, PixelColour) 
			for i in range (8+HealthPixels,16 ,1):
				strip.setPixelColor(i, neopixel.Color(0,0,0)) # Turn pixel white when finished

	strip.show()
