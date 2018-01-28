# mainESP1.py - esp8266 board
#
# Master program for ESP1
#    reads a DHT22 temperature and humidity sensor and
#    an SHT-31D. It then
#    send the data out using a UDP packet to the local network
#
# 1/29/2017 - sjc
# 7/10/2017 - sjc - rewrite to increase functionality
# 11/10/2017 - sjc - Add a DS18B20 waterproof temp sensor
#

# imports needed
import dht
import machine
import time
import socket
import sht31
import network
import onewire, ds18x20

# Some useful values
loopTime = 1  # loop every 60s
count = 1

# Pin definitions
# sht31
sdaPin = 4
sclPin = 5
# DHT22
dhtPin = 13
# onewire
owPin = 0

# Set up objects for reading sensors

# DHT22
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

# For DS18B20 set up onewire
ds = ds18x20.DS18X20(onewire.OneWire(machine.Pin(owPin)))
roms = ds.scan()
dsTempUnit = 'C'
dsTempId = '01005'


# set up socket
wlan = network.WLAN(network.STA_IF)
hostip = wlan.ifconfig()[0]
port = 10000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (hostip,port)
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
            message = 'ESP1'
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
            #    message = "ESP1:"
            #     To smooth spikes, average count measurements and then send

            #     Initialize measurements
            message = "ESP1:"

            dhttempC = 0.0
            dhthumidity = 0.0
            shttempF = 0.0
            shthumidity = 0.0
            dstempC = 0.0

            for i in range(count):

                try:
                    # Read dht22 - reads in C and RH
                    dht22.measure()

                    dhttempC += dht22.temperature()
                    dhthumidity += dht22.humidity()

                    #Read the sht31 - reads in F and RH
                    tempF, humidity = shtBoard.get_temp_humi(celsius=False)

                    shttempF += tempF
                    shthumidity += humidity

                    # Read DS18B20
                    ds.convert_temp()
                    time.sleep_ms(750)
                    dstempC += ds.read_temp(roms[0])


                except:
                    print('Error')

                time.sleep(loopTime)

            # Now send the average

            try:
                #print to terminal (if connected) for debugging
                print("DHTTemp: %f  DHTHumidity: %f " % (dhttempC/count, dhthumidity/count))
                print("SHTTemp: %f  SHTHumidity: %f " % (shttempF/count, shthumidity/count))
                print("DSTemp: %f " % (dstempC/count))

                message = message + "{:s}:{:3.2f}:{:s}:".format(dhtTempId,dhttempC/count,dhtTempUnit)
                message = message + "{:s}:{:3.2f}:{:s}:".format(dhtHumId, dhthumidity/count, dhtRHUnit)

                message = message + "{:s}:{:3.2f}:{:s}:".format(shtTempId,shttempF/count,shtTempUnit)
                message = message + "{:s}:{:3.2f}:{:s}:".format(shtHumId, shthumidity/count, shtRHUnit)

                message = message + "{:s}:{:3.2f}:{:s}".format(dsTempId,dstempC/count,dsTempUnit)

            except:
                message = "Error"
                pass

        sock.sendto(message, address)
    except:
        pass
