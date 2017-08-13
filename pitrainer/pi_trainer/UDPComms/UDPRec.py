import socket
import socketserver
import threading
import xml.etree.ElementTree as ElementTree

# Project modules
import config.config as config


# Class to handle receiving UDP messages, including messages from Pi Fighter to provide Haptic feedback to the fighter.
class UDPRecHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantianted once per connection to the server, and must
    override the handle() method to implement communication to the
    client.

    """

    def handle(self):

        # self.request is the UDP socket connected to the client
        self.data = self.request[0].strip()
        socket = self.request[1]

        # Decode to ASCII so it can be processed.
        clientstr = self.data.decode('ascii')

        # Put the data into an XML Element Tree
        try:
            print(clientstr)
            client_element = ElementTree.fromstring(clientstr)

            # If Attack received, then calcualte the effect on the opponent.

            if (client_element.tag == 'OpponentAttack'):

                print(client_element.text)

                # Figure out the percent vibration for rumbling.  
                percent_vibe = float(float(client_element.text) / 16.0 * 100)
                print(percent_vibe)

                rumblestr = "<Rumble><Vib0Str>{}</Vib0Str><Vib1Str>{}</Vib1Str><Vib2Str>{}</Vib2Str><MsDuration>{}</MsDuration></Rumble>".format(
                    int(percent_vibe), int(percent_vibe), int(percent_vibe), int(2 * percent_vibe))

                # Put it into the Rumble Q for activating vibrators.  
                config.RumbleQ.put_nowait(rumblestr)

            else:
                print("Can't process string {}".format(clientstr))

        except:
            print("EXCEPTION: Trouble Processing String: {}".format(clientstr))
            raise ()


# Class to handle the UDP Comms - manages the attacks and other messages from the Pi Fighter App, etc.
class UDPRecThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        print("Starting " + self.name)

        try:
            # print ("UDP")
            hostname = socket.gethostbyname("KirbyPiZeroW")
            # hostname = "localhost"
            print(socket.getfqdn())

            print("UDP - Trying again", hostname, int(config.config_file['UDP']['PI_TRAINER_PORT']))

            # Create the UDP server.
            udp_server = socketserver.UDPServer((hostname, int(config.config_file['UDP']['PI_TRAINER_PORT'])), UDPRecHandler)

            # Activate the server; this will keep running until you
            # interrupt the program with Ctrl-C
            udp_server.serve_forever()

        except:
            print("UDP Exception")
            raise


        finally:
            udp_server.close()
            exit()
