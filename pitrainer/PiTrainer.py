#!/usr/bin/python3

# Standard Modules
import time

# Custom packages
import rumble.rumble as rumble  # Controls Vibrators
import config.config as config  # Config python file to share common stuff like global variables.
import UDPComms.UDPRec as UDPRec  # UDP Comms
import DisplayHandler.DisplayHandler as DisplayHandler  # Handles the display.
import skip.skip_counter as skip_counter
import Accel.Accel as Accel

# Short test to confirm each of the vibrators is working.
for i in range(0, 3):
    print("Vibrator ", i)

    VibrStrength = [0, 0, 0]
    for j in range(20, 105, 20):
        VibrStrength[i] = j
        RumbleCmd = str(
            "<Rumble><Vib0Str>{}</Vib0Str><Vib1Str>{}</Vib1Str><Vib2Str>{}</Vib2Str><MsDuration>200</MsDuration></Rumble>".format(
                VibrStrength[0], VibrStrength[1], VibrStrength[2]))
        config.RumbleQ.put_nowait(RumbleCmd)

    VibrStrength = [0, 0, 0]
    for j in range(20, 105, 20):
        VibrStrength[0] = j
        VibrStrength[1] = j
        VibrStrength[2] = j

        RumbleCmd = str(
            "<Rumble><Vib0Str>{}</Vib0Str><Vib1Str>{}</Vib1Str><Vib2Str>{}</Vib2Str><MsDuration>200</MsDuration></Rumble>".format(j,j,j))

        config.RumbleQ.put_nowait(RumbleCmd)

if __name__ == "__main__":

    accel = Accel.I2C_Accelorometer()

    try:

        # Start up the various threads.

        # Skip Counting Thread.  Needs Accelerometer
        skip_count_thread = skip_counter.SkipCountThread(1, "Skip Counter", 1, accel)
        skip_count_thread.start()

        # Display Thread.
        SkipCountDisplayThread = DisplayHandler.CountDisplayThread(1, "Count Display Thread", 1)
        SkipCountDisplayThread.start()

        # Start up the UDP Rec Thread.
        UDPRecThreadHdl = UDPRec.UDPRecThread(1, "UDP Rec Thread", 1)
        UDPRecThreadHdl.start()

        # Start up the Rumble Thread.
        RumbleThreadHdl = rumble.RumbleThread(1, "Rumble Thread", 1)
        RumbleThreadHdl.start()

        while (1):
            # Build an object of the Accel Class
            0

    except KeyboardInterrupt:
            print("Fine - quit see if I care - jerk")

            # Asks the thread to finish nicely.
            skip_count_thread.join()
            SkipCountDisplayThread.join()
            UDPRecThreadHdl.join()
            RumbleThreadHdl.join()
            config.pi.stop()

            exit()
