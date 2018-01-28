# main.py - esp8266 board
#
# Master program to read DHT22 temperature and humidity sensor and
# send the data out using a UDP packet to the local network
#
# 10/20/2016 - sjc
#
#

# imports needed
import dht
import machine
import time
import socket

# Some useful values
dhtPin = 13    # DHT wired to pin 13
loopTime = 60  # loop every 30s

# Now set up object for reading sensor

dht22 = dht.DHT22(machine.Pin(dhtPin))

# set up socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ("192.168.1.226", 21567)

# Main loop to get readings

while True:
    dht22.measure()

    tempC = dht22.temperature()
    humidity = dht22.humidity()

    print("Temp: %f  Humidity: %f " % (tempC, humidity))

#    sock.sendto("ESP1:"+str(tempC)+":"+str(humidity), server_address)
    message = "ESP1:{:3.2f}:{:3.2f}".format(tempC, humidity)

    sock.sendto(message, server_address)

    time.sleep(loopTime)


