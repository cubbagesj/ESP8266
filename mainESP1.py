# main.py - esp8266 board
#
# Master program for ESP1
#    reads a DHT22 temperature and humidity sensor and
#    an SHT-31D. It then 
#    send the data out using a UDP packet to the local network
#
# 1/29/2017 - sjc
#
#

# imports needed
import dht
import machine
import time
import socket
import sht31

# Some useful values
dhtPin = 13    # DHT wired to pin 13
loopTime = 60  # loop every 60s
count = 5

sdaPin = 4
sclPin = 5

# For DHT22 - This sensor does not seem too accurate

# Set up object for reading sensors

dht22 = dht.DHT22(machine.Pin(dhtPin))
dhtTempUnit = 'C'
dhtRHUnit = 'RH'
dhtTempId = '01001'
dhtHumId = '01002'

# for sht31 set up i2c
i2c = machine.I2C(sda = machine.Pin(sdaPin), scl = machine.Pin(sclPin))
shtBoard = sht31.SHT31(i2c)
shtTempUnit = 'F'
shtRHUnit = 'RH'
shtTempId = '01003'
shtHumId = '01004'


# set up socket

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
message = "ESP1:"

# Main loop to get readings

while True:
    message = "ESP1:"
    # To smooth spikes, average 5 measurements and then send
    # Initialize measurments
    dhttempC = 0.0
    dhthumidity = 0.0
    shttempF = 0.0
    shthumidity = 0.0
    
    for i in range(count):
        
        try:
    
            dht22.measure()
    
            dhttempC += dht22.temperature()
            dhthumidity += dht22.humidity()
     
            #Read the sht31 - reads in F and RH
            tempF, humidity = shtBoard.get_temp_humi(celsius=False)
    
            shttempF += tempF
            shthumidity += humidity
                        
     
     
    
    
        except:
            print('Error')
    
        time.sleep(loopTime)
        
    # Now send the average

    try:    
        #print to terminal (if connected) for debugging
        print("DHTTemp: %f  DHTHumidity: %f " % (dhttempC/count, dhthumidity/count))
        print("SHTTemp: %f  SHTHumidity: %f " % (shttempF/count, shthumidity/count))
        
        message = message + "{:s}:{:3.2f}:{:s}:".format(dhtTempId,dhttempC/count,dhtTempUnit)
        message = message + "{:s}:{:3.2f}:{:s}:".format(dhtHumId, dhthumidity/count, dhtRHUnit)
    
        message = message + "{:s}:{:3.2f}:{:s}:".format(shtTempId,shttempF/count,shtTempUnit)
        message = message + "{:s}:{:3.2f}:{:s}".format(shtHumId, shthumidity/count, shtRHUnit)
    
        sock.sendto(message, server_address)

    except:
        pass
    
