#-----------------------------------------------------------------------------------------
# ff32ds18B20.py by Paul Merkx 12/7/14
# About:
# Simple library for reading 1-wire DS18B20 temperature device through
# FlyFish technology FF32 multi purpose interface chip (www.flyfish-tech.com)
# Limitations:
# - Single 1-wire device at FF32 port
# - Fixed (default) 12 bit resolution (and thus "slow" 750ms conversion)
#
# Acknowledgements:
# Based on 1-wire demo supplied from FlyFish-tech
#
# 
# Wiring:
#  ____         ______            _________
# |    |       |      |B2*-----DQ|         |
# |Rpi |-USB---| FF32 |          | Maxim   |
# |    |       |      |GND----GND| DS18B20 |
# |____|       |______|Vdd----Vdd|_________|   (* B2 can be any FF32 general purpose pin)
#
# The datasheet for the DS18B20 is available at
# http://datasheets.maximintegrated.com/en/ds/DS18B20.pdf
#
#----------------------------------------------------------------------------------------------

import pyff32

class DS18B20:
    SCRATCH = 9     # Number of bytes in scratchpad for particular device
    CRC_CHECK = bytearray([0, 94, 188, 226, 97, 63, 221, 131, 194, 156, 126, 32, 
        163, 253, 31, 65,157, 195, 33, 127, 252, 162, 64, 30, 95, 1, 227, 189, 62, 96, 130, 220,
        35, 125, 159, 193, 66, 28, 254, 160, 225, 191, 93, 3, 128, 222, 60, 98,
        190, 224, 2, 92, 223, 129, 99, 61, 124, 34, 192, 158, 29, 67, 161, 255,
        70, 24, 250, 164, 39, 121, 155, 197, 132, 218, 56, 102, 229, 187, 89, 7,
        219, 133, 103, 57, 186, 228, 6, 88, 25, 71, 165, 251, 120, 38, 196, 154,
        101, 59, 217, 135, 4, 90, 184, 230, 167, 249, 27, 69, 198, 152, 122, 36,
        248, 166, 68, 26, 153, 199, 37, 123, 58, 100, 134, 216, 91, 5, 231, 185,
        140, 210, 48, 110, 237, 179, 81, 15, 78, 16, 242, 172, 47, 113, 147, 205,
        17, 79, 173, 243, 112, 46, 204, 146, 211, 141, 111, 49, 178, 236, 14, 80,
        175, 241, 19, 77, 206, 144, 114, 44, 109, 51, 209, 143, 12, 82, 176, 238,
        50, 108, 142, 208, 83, 13, 239, 177, 240, 174, 76, 18, 145, 207, 45, 115,
        202, 148, 118, 40, 171, 245, 23, 73, 8, 86, 180, 234, 105, 55, 213, 139,
        87, 9, 235, 181, 54, 104, 138, 212, 149, 203, 41, 119, 244, 170, 72, 22,
        233, 183, 85, 11, 136, 214, 52, 106, 43, 117, 151, 201, 74, 20, 246, 168,
        116, 42, 200, 150, 21, 75, 169, 247, 182, 232, 10, 84, 215, 137, 107, 53])

    def __init__(self, onewirepin):
        # Set 1-Wire bus pin
        self.onewirepin = onewirepin
        with pyff32.FF32() as ff32:
            try:
                ff32.set1WirePin(self.onewirepin)
                self.init_success=True
            except Exception as ex:
                print("*** Error (Set1WirePin): " + ex.message)
                self.init_success=False

            
    #	This procedure calculates the Maxim 1-Wire CRC of all bytes passed to it.
    #   The result True is returned when calculated CRC equals CRC passed in last byte.
    #   Based on http://www.maximintegrated.com/app-notes/index.mvp/id/27
    def Check_CRC(self, bytes):
        CRC = 0
        for i in range (0,self.SCRATCH-1):
            CRC = self.CRC_CHECK[CRC ^ bytes[i]]
        return ((CRC == bytes[self.SCRATCH-1]))            
     
    # Read_Temp returns the temperature in degrees celsius
    def Read_Temp(self):
        with pyff32.FF32() as ff32:
            # Write to 1-Wire device (DS18B20 - initiate temperature conversion)
            # Uses Skip ROM command: only to be used when a single device is on the bus
            bytes = bytearray([0xCC, 0x44])
            try:
                ff32.write1WireBus(bytes)
            except Exception as ex:
                print("*** Error (Write1WireBus): " + ex.message)
                
            # Read scratchpad from DS18B20 
            bytes = bytearray([0xCC, 0xBE])
            try:
                bytes = ff32.read1WireBus(self.SCRATCH, bytes)
            except Exception as ex:
                print("*** Error (Read1WireBus): " + ex.message)

            # Check if CRC over scratchpad confirms valid data received  
            if self.Check_CRC(bytes):
                temperature=(bytes[1] * 256 + bytes[0]) * 0.0625
            else:
                # just return nonsense result to report invalid data
                temperature=200
            return temperature    
