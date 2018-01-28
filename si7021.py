from time import sleep_ms
from machine import Pin, I2C

# Default Address
SI7021_I2C_DEFAULT_ADDR = 0x40

# Commands
CMD_MEASURE_RELATIVE_HUMIDITY_HOLD_MASTER_MODE = 0xE5
CMD_MEASURE_RELATIVE_HUMIDITY = 0xF5
CMD_MEASURE_TEMPERATURE_HOLD_MASTER_MODE = 0xE3
CMD_MEASURE_TEMPERATURE = 0xF3
CMD_READ_TEMPERATURE_VALUE_FROM_PREVIOUS_RH_MEASUREMENT = 0xE0
CMD_RESET = 0xFE
CMD_WRITE_RH_T_USER_REGISTER_1 = 0xE6
CMD_READ_RH_T_USER_REGISTER_1 = 0xE7
CMD_WRITE_HEATER_CONTROL_REGISTER = 0x51
CMD_READ_HEATER_CONTROL_REGISTER = 0x11

class Si7021(object):
    def __init__(self, i2c_addr = SI7021_I2C_DEFAULT_ADDR):
        self.addr = i2c_addr
        self.cbuffer = bytearray(2)
        self.cbuffer[1] = 0x00
        self.i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)

    def write_command(self, command_byte):
        self.cbuffer[0] = command_byte
        self.i2c.writeto(self.addr, self.cbuffer)

    def readTemp(self):
        self.write_command(CMD_MEASURE_TEMPERATURE)
        sleep_ms(25)
        temp = self.i2c.readfrom(self.addr,3)
        temp2 = temp[0] << 8
        temp2 = temp2 | temp[1]
        return (175.72 * temp2 / 65536) - 46.85

    def readRH(self):
        self.write_command(CMD_MEASURE_RELATIVE_HUMIDITY)
        sleep_ms(25)
        rh = self.i2c.readfrom(self.addr, 3)
        rh2 = rh[0] << 8
        rh2 = rh2 | rh[1]
        return (125 * rh2 / 65536) - 6
