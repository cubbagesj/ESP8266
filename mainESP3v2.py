# mainESP3.py - esp8266 board
#
# Master program for ESP3
#    reads a DHT22 temperature and humidity sensor and
#    the garage door sensors. It then
#    send the data out using a UDP packet to the local network
#
# Duplicated from mainESP2
#
# 1/27/2018 - sjc
#
#

# imports needed
import dht
import machine
import time
import socket
import network

# Some useful values
dhtPin = 13    # DHT wired to pin 13
loopTime = 1  # Short pause single measurements
count = 1       # single measurement


# For DHT22 - This sensor does not seem too accurate

# Set up object for reading sensors

dht22 = dht.DHT22(machine.Pin(dhtPin))
dhtTempUnit = 'C'
dhtRHUnit = 'RH'
dhtTempId = '03001'
dhtHumId = '03002'

# Setup the door sensorimport machine
door1 = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)

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
            message = 'ESP3'
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
            message = "ESP3:"

            # To smooth spikes, average count measurements and then send
            # Initialize measurements

            dhttempC = 0.0
            dhthumidity = 0.0

            for i in range(count):

                try:

                    # Read DHT22 - reads in C and RH
                    dht22.measure()

                    dhttempC += dht22.temperature()
                    dhthumidity += dht22.humidity()

                    # Read the door sensor
                    d1value = door1.value()
                    
                except:
                    print('Error')

                time.sleep(loopTime)

            try:

                # Print to terminal (if connected) for debugging
                print("DHTTemp: %f  DHTHumidity: %f " % (dhttempC/count, dhthumidity/count))

                message = message + "{:s}:{:3.2f}:{:s}:".format(dhtTempId,dhttempC/count,dhtTempUnit)
                message = message + "{:s}:{:3.2f}:{:s}:".format(dhtHumId, dhthumidity/count, dhtRHUnit)

            except:
                message = "Error"
                pass

        sock.sendto(message, address)
    except:
        pass
