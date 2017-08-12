# Standard Libraries
import threading
import xml.etree.ElementTree as ElementTree
import time

# Project Libraries.
import config.config as config

# GPIO Definitions for the vibrators (3 count)
Vibrators = [17, 27, 22]

# Thread to handle Rumbling on command.  The main thread handling run just loops
# continuously dealing with requests to "Rumble" - this operates up to three
# Vibrators attached to the Pi via PWM.
class RumbleThread (threading.Thread):


    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter


    # Deals with all the requests to Rumble
    def run(self):
        #global RumbleQ

        ms_duration = 0

        print ("Starting " + self.name)

        while(1):
            # Do the Rumble as required by the Queue.
            # Check the Queue - if something in there, then process them in turn.
            if config.RumbleQ.empty() == False:
                rumble_str = config.RumbleQ.get_nowait()

                # Accept XML string that specifies rumble information - each Rumble XML needs to specify the strength
                # of each of the three vibrators, which may be 0.  Number of ms to rumble for is also required.
                # <Rumble><Vib0Str>0-100</Vib0Str><Vib1Str>0-100</Vib1Str><Vib2Str>0-100</Vib2Str><MsDuration>0-10000</MsDuration></Rumble>

                print (rumble_str)

                # Process the XML rumble request via the Element Tree library.
                RumbleElement = ElementTree.fromstring(rumble_str)

                # If Rumble - process it.
                VibeStr =[0,0,0] # Init
                if (RumbleElement.tag == 'Rumble'):

                    # Read through all the information, extracting the data required to rumble.
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
                            ms_duration = int(Child.text)

                    # Run the requested Vibrations

                    for i in range(0,3):

                        # Important to check the range - set to max if exceeded.
                        PWM = int(int(VibeStr[i])*255/100)
                        if (PWM > 255):
                            PWM =255

                        #print ("***", PWM) # debug - remove later.
                        config.pi.set_PWM_dutycycle(Vibrators[i], PWM)

                    # sleep as specified - rumble is ongoing at this point.
                    time.sleep(float(ms_duration/1000))

                    # Turn vibrators off.
                    for i in range(0,3):
                        config.pi.set_PWM_dutycycle(Vibrators[i], 0)
                        time.sleep(.3)
                else:
                    print("****Unrecognised command - rumble thread - ignoring - not worth halting")

        print ("Exiting " + self.name)
        exit()