# Standard Modules
import queue
import socket
import threading
import time

# Scrollphathd from Pimoroni
import scrollphathd
from scrollphathd.fonts import font5x7

# Project Modules
import config.config as config

# Create a queue for talking between the threads
UDP_q = queue.Queue()


# Thread to handle outputting to the OLED screen and sending to the server.
# - to avoid spending too much time blocked on this.
class CountDisplayThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        print("Starting " + self.name)
        # print_time(self.name, self.counter, 5)

        # Some initialisation
        last_display_time = time.time()
        skip_count = 0

        print(config.SERVER_HOST, config.SERVER_PORT)

        while (1):
            # Print to the OLED Screen - Get the information from the Queue whenever available,
            # but only update OLED screen once in a while Screen is too slow for many updates.
            if not UDP_q.empty():
                skip_count = UDP_q.get_nowait()

                skip_count_info = "<Skip><SkipCount>{:d}</SkipCount></Skip>".format(skip_count)

                try:
                    # Open socket and send data - Open it each time as there were problems when comms wasn't great.
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as ServerSocket:
                        # Connect to server and send data
                        ServerSocket.setblocking(False)
                        ServerSocket.sendto(bytes(skip_count_info, "utf-8"), (config.SERVER_HOST, config.SERVER_PORT))
                except:
                    print("Send Failure - who cares?  Not me.")

            skip_count_str = "{:d}".format(skip_count)
            elapsed_time = time.time() - last_display_time

            if elapsed_time > 2:
                scrollphathd.clear()
                scrollphathd.write_string(skip_count_str, x=0, y=0, font=font5x7, brightness=0.5)
                scrollphathd.show()
                last_display_time = time.time()

        print("Exiting " + self.name)
        exit()