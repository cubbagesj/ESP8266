# main.py - esp8266 board
#
# Master program for ESP2
#    reads a DHT22 temperature and humidity sensor and
#    an Si7021. It then 
#    send the data out using a UDP packet to the local network
#
# Modified to change data message
#
# 3/13/2017 - sjc
#
#

# imports needed
import dht
import machine
import time
import socket
import si7021

# Some useful values
dhtPin = 13    # DHT wired to pin 13
loopTime = 60  # loop every 30s
count = 5


# For DHT22 - This sensor does not seem too accurate

# Set up object for reading sensors

dht22 = dht.DHT22(machine.Pin(dhtPin))
dhtTempUnit = 'C'
dhtRHUnit = 'RH'
dhtTempId = '02001'
dhtHumId = '02002'

# For si7021 - using default I2C address
SiBoard = si7021.Si7021() 
siTempUnit = 'C'
siRHUnit = 'RH'
siTempId = '02003'
siHumId = '02004'


# set up socket - Using cubpi9 as the base station IP:192.168.1.226

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ("192.168.1.210", 21567)

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
message = "ESP2:"


# Main loop to get readings

while True:
    message = "ESP2:"
    
    # To smooth spikes, average 5 measurements and then send
    # Initialize measurements
    dhttempC = 0.0
    dhthumidity = 0.0
    SitempC = 0.0
    Sihumidity = 0.0
    
    for i in range(count):
        
        try:
   
            # Read DHT22 - reads in C and RH
            dht22.measure()
        
            dhttempC += dht22.temperature()
            dhthumidity += dht22.humidity()
        
            # Read the si7021 - reads in C and RH
            SitempC += SiBoard.readTemp()
            Sihumidity += SiBoard.readRH() 
            
        except:
            print('Error')
            
        time.sleep(loopTime)
    
    try:

        # Print to terminal (if connected) for debugging
        print("DHTTemp: %f  DHTHumidity: %f " % (dhttempC/count, dhthumidity/count))
        print("SiTemp: %f  SiHumidity: %f " % (SitempC/count, Sihumidity/count))
    
        message = message + "{:s}:{:3.2f}:{:s}:".format(dhtTempId,dhttempC/count,dhtTempUnit)
        message = message + "{:s}:{:3.2f}:{:s}:".format(dhtHumId, dhthumidity/count, dhtRHUnit)

        message = message + "{:s}:{:3.2f}:{:s}:".format(siTempId,SitempC/count,siTempUnit)
        message = message + "{:s}:{:3.2f}:{:s}".format(siHumId, Sihumidity/count, siRHUnit)

        sock.sendto(message, server_address)
    except:
        print("Error")
        pass


