# Standard Modules
import threading
import time
import datetime
import math
import logging

# Project packages.
import Accel.Accel as Accel
import config.config as config
import DisplayHandler.DisplayHandler as DispHandler

# Thread to handle skipping count.
class SkipCountThread(threading.Thread):

    # Max acceleration rate in the display period - initial values to start.
    max_accel = 0
    sample_num = 0
    skip_count = 0

    def __init__(self, threadID, name, counter, accel):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.accel = accel # reference to accelerometer

    def run(self):
        print("Starting " + self.name)

        while (1):
            # Grab Accelerometer Data
            scaled_accel = self.accel.get_scaled_accel_values()  # X,Y,Z acceleration

            date_string = datetime.datetime.now().date()
            time_string = datetime.datetime.now().time()

            total_accel = math.sqrt(scaled_accel[0] ** 2 + scaled_accel[1] ** 2 + scaled_accel[2] ** 2)

            # Set the sign of the acceleration by a simple sum of the components
            if ((scaled_accel[0] + scaled_accel[1] + scaled_accel[2]) < 0):
                total_accel = -1 * total_accel

            log_str = "{},{},{:2.3},{:2.3f}, {:2.3f}, {:2.3f}".format(date_string, time_string,
                        scaled_accel[0], scaled_accel[1], scaled_accel[2], total_accel)

            logging.info(log_str)

            # Update Accel if needed
            if abs(total_accel) > self.max_accel:
                self.max_accel = abs(total_accel)

            # If Skip is detected due to the threshold being exceeded, then update the skip count
            # and put it into the queue for processing by the OLED thread.  OLED thread is too slow to
            # keep up with the skipping and print to the OLED which has a low refresh rate.
            if self.sample_num % config.DISPLAY_FREQ == 0:
                # print ("Max :", MaxAccel)
                if self.max_accel > config.SKIP_THRESHOLD:
                    self.skip_count = self.skip_count + 1
                    print(self.skip_count)

                    # Put into the queue for processing.
                    DispHandler.UDP_q.put_nowait(self.skip_count)

                self.max_accel = 0

            time.sleep(config.SAMPLE_SLEEP / 1000)
            self.sample_num += 1