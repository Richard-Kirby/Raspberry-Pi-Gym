# Raspberry-Pi-Gym
A starter workout gym built using a Raspberry Pi and various cheap components available from various websites.

This was presented to Raspberry Pint in London UK on 29 November 2016.  A refresh to the original presentation was done on 28 Feb 2017.  See presentation at the link below.  

https://prezi.com/d7vwru_fkcml/birth-of-pi-gym-pigym-v03/T

The gym provides several components, including:
- A heavy bag workout, which sends suggested attacks via neopixels to the user.  The acceleration of the heavy bag is measured using a MPU-6050 6 degree of freedom accelerometer.  The acceleration is indicated graphically onto a cheap/nasty 8x8 SPI LED Matrix as well as transmitted (via UDP/IP messages) to a server for further use, such as to use in a fight with an imaginary or real opponent(s) connected to the same server.  The Virtual opponent as well as the current player's health are displayed on 2 x 8 pixel neostrips.   

- A Skip application that provides suggested timing for the skipping to the user via a cheap/nasty LED strip.  It drives a second LED strip for stepping.  The LED Strip is a SMD 5050 RGB strip - this is not a neopixel strip.  It is a 12 Volt strip that can be driven from the Raspberry Pi using the PIGPIO library.  The outputs for the RGB connect to the base of an NPN transistor and send PWM pulses to switch the strip to ground. 

- An application for a Raspberry Pi that measures the number of skips above a threshold and sends each skip to the same Server.  

All applications are configurable to allow tuning and they all create their own logs which can be used for other programs or analysis.  

Really this is a _still_ an early cut of the Pi Gym suite - a lot of work is still required, but it does contain some basic functionality as described above.  

NOTE: uses https://pypi.python.org/pypi/rpi_ws281x/2.0.3 - note that you have to turn off the Pi Audio board for the neopixel strips
to work properly. As per https://github.com/jgarff/rpi_ws281x/wiki - You must disable the on-board audio by blacklisting the Broadcom audio kernel module.
