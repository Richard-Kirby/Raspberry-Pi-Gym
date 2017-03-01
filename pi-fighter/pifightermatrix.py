
#SPI LED Matrix stuff -
import max7219.led as led
from max7219.font import proportional, SINCLAIR_FONT, TINY_FONT, CP437_FONT
import time


def Setup():
	global device 
	
	device = led.matrix()

	# Let the user know about to start
	device.orientation(180) # SPI is mounted upside down for cabling reasons.


# Writing the Intro String to the Matrix - gives time to get ready. 
def Intro(IntroStr= "Pi-Fighter"):

	device.brightness(15)

	device.show_message(IntroStr, font=proportional(CP437_FONT), delay = 0.04)

	# Countdown 	
	for i in range(5,-1,-1):
		Str = ("{}".format(i))
		device.show_message(Str, font=proportional(CP437_FONT), delay = 0.04)
		time.sleep(.4)

# Write a string to the Matrix. 
def DisplayStr(WriteStr):

	device.brightness(15)

	device.show_message(WriteStr, font=proportional(CP437_FONT), delay = 0.04)

		
		

def DrawPattern(PatternId, Brightness):


	if (Brightness >15):
		Brightness = 15
		
	Patterns =[
	[[0,0,0,0,0,0,0,1],
	[0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0]],

	[[0,0,0,0,0,0,1,1],
	[0,0,0,0,0,0,1,1],
	[0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0]], 

	[[0,0,0,0,0,1,1,1],
	[0,0,0,0,0,1,1,1],
	[0,0,0,0,0,1,1,1],
	[0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0]], 

	[[0,0,0,0,1,1,1,1],
	[0,0,0,0,1,1,1,1],
	[0,0,0,0,1,1,1,1],
	[0,0,0,0,1,1,1,1],
	[0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0]], 

	[[0,0,0,1,1,1,1,1],
	[0,0,0,1,1,1,1,1],
	[0,0,0,1,1,1,1,1],
	[0,0,0,1,1,1,1,1],
	[0,0,0,1,1,1,1,1],
	[0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0]], 

	[[0,0,1,1,1,1,1,1],
	[0,0,1,1,1,1,1,1],
	[0,0,1,1,1,1,1,1],
	[0,0,1,1,1,1,1,1],
	[0,0,1,1,1,1,1,1],
	[0,0,1,1,1,1,1,1],
	[0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0]], 

	[[0,1,1,1,1,1,1,1],
	[0,1,1,1,1,1,1,1],
	[0,1,1,1,1,1,1,1],
	[0,1,1,1,1,1,1,1],
	[0,1,1,1,1,1,1,1],
	[0,1,1,1,1,1,1,1],
	[0,1,1,1,1,1,1,1],
	[0,0,0,0,0,0,0,0]], 

	[[1,1,1,1,1,1,1,1],
	[1,1,1,1,1,1,1,1],
	[1,1,1,1,1,1,1,1],
	[1,1,1,1,1,1,1,1],
	[1,1,1,1,1,1,1,1],
	[1,1,1,1,1,1,1,1],
	[1,1,1,1,1,1,1,1],
	[1,1,1,1,1,1,1,1]]
	
	]

	device.brightness(Brightness)
	for i in range (0,8):
		for j in range (0,8):
			device.pixel(i, j, Patterns[PatternId][i][j], redraw=False)
	device.flush()
