# mainESP4.py - esp8266 board
#
# Master program for ESP4
#    reads a garage door sensor. It then
#    send the data out using a UDP packet to the local network
#
# Duplicated from mainESP3
#
# This board is using circuitpython instead of micropython
#
# 2/17/2018 - sjc
#
#

# imports needed
import board
import busio
import time
import socket
import network
from digitalio import DigitalInOut, Direction, Pull


# Some useful values
ssid = 'cubnet'
password = 'almond11'


door1Unit = 'Bool'
door1ID = '04001'


# Setup the door sensors
door1 = DigitalInOut(board.GPIO12)
door1.direction = Direction.INPUT
door1.pull = Pull.UP

# set up networking
wlan = network.WLAN(network.STA_IF)
if not wlan.isconnected():
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        pass
print("Connected! IP = ", wlan.ifconfig()[0])

# Get local IP address
hostip = wlan.ifconfig()[0]
port = 10000

# Open a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (hostip, port)
sock.bind(server_address)

# Main loop
#
# The main loop waits for a packet to arrive and then takes action
# based on the command in the packet message

while True:
    print('Waiting....')
    try:
        command, address = sock.recvfrom(2048)

        # echo what we got
        print('cmd recvd: %s' % command)

        # Now main loop for commands
        # micropython recvfrom returns a byte array and not a string
        # so for simplicity just use byte commands

        if command == b'\xAA':
            # Base is looking for nodes, reply with name
            print('PING')
            message = 'ESP4'
        elif command == b'\xBB':
            # Query for data
            print('Measuring')
            # Set up message Header
            #
            # Standard message format to make reading multiple sensors easier
            #
            # Format is:
            #    1. ESP## - ESP number 2-digit number i.e. ESP01 (up to 99 sensors)
            #    2. sensorid - made of esp# and 3-digit sensor num. i.e. 01001 (board 1, sens 1)
            #    3. reading - float in native units
            #    4. units - unit abbreviation (i.e. C, F, RH, etc...)
            #
            #   Then repeat 2-4 for each sensor. Fields seperated by ':' character
            #

            # Main loop to get readings
            message = "ESP4:"

            # To smooth spikes, average count measurements and then send
            # Initialize measurements

            for i in range(count):

                try:

                    # Read the door sensors
                    door1Value = door1.value

                except:
                    print('Error')

                time.sleep(loopTime)

            try:

                # Print to terminal (if connected) for debugging
                print("door1Value: %f " % (door1Value))

                message = message + "{:s}:{:d}:{:s}".format(door1ID, door1Value, door1Unit)                message = message + "{:s}:{:d}:{:s}".format(door2ID, door2Value, door2Unit)

            except:
                message = "Error"
                pass

        sock.sendto(message, address)
    except:
        pass
