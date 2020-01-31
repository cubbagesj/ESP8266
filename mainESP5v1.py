# mainESP5.py - esp8266 board
#
# Master program for ESP5
#    Reads a VL53L0x time-of-flight sensor. It then
#    send the data out using a UDP packet to the local network
#
#
# 1/30/2020 - sjc
#
#

# imports needed
from machine import I2C, Pin
import vl53l0x
import time
import socket
import network


dist1Unit = 'mm'
dist1ID = '05001'

# Setup i2c to talk to sensor
i2c = I2C(-1, Pin(5), Pin(4))
sensor = vl53l0x.VL53L0X(i2c)

# set up socket
# Get local IP address
wlan = network.WLAN(network.STA_IF)
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
            message = 'ESP5'
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
            message = "ESP5:"

            distance = sensor.read()

            try:

                # Print to terminal (if connected) for debugging
                print("Distance (mm): %d " % (distance))

                message = message + "{:s}:{:d}:{:s}".format(dist1ID,distance,dist1Unit)

            except:
                message = "Error"
                pass

        sock.sendto(message, address)
    except:
        pass
