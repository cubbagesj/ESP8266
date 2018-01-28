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

dht11 = dht.DHT11(machine.Pin(dhtPin))

# set up socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ("192.168.1.226", 21567)

# Main loop to get readings

while True:
    dht11.measure()

    tempC = dht11.temperature()
    humidity = dht11.humidity()

    print("Temp: %f  Humidity: %f " % (tempC, humidity))

    message = "ESP2:{:3.2f}:{:3.2f}".format(tempC, humidity)

    sock.sendto(message, server_address)

    time.sleep(loopTime)


