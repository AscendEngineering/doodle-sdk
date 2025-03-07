from doodle_sdk.doodle_radio import Doodle
import doodle_sdk.stats as stats
import time

if __name__ == '__main__':

    # Connect to radio
    doodle1 = Doodle(ip="10.223.84.236", user="user", password="DoodleSmartRadio")
    doodle1_connected = doodle1.connect()

    doodle1.set_frequency(2450)
    doodle1.set_channel(12)
    
    print("Frequency:", doodle1.get_frequency())
    print("Channel:", doodle1.get_channel())

    doodle1.set_frequency(915)
    doodle1.set_channel(10)



    print("Frequency:", doodle1.get_frequency())
    print("Channel:", doodle1.get_channel())
    print("Channel Width:", doodle1.get_channel_width())
    print("Version:", doodle1.get_firmware_version())

    print('------------------------')

    # Set the frequency, channel, bandwidth
    # doodle1.set_frequency(2450)
    # doodle1.set_channel(10)
    # doodle1.set_channel_width(5)

    print("Frequency:", doodle1.get_frequency())
    print("Channel:", doodle1.get_channel())
    print("Channel Width:", doodle1.get_channel_width())
    print("Version:", doodle1.get_firmware_version())
