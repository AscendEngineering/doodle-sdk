from doodle_sdk.doodle_radio import Doodle
import doodle_sdk.stats as stats
import time

if __name__ == '__main__':

    # Connect to radio
    doodle1 = Doodle(ip="10.223.108.26", user="root", password="DoodleSmartRadio")
    doodle1_connected = doodle1.connect()
    print(doodle1_connected) 

    # Get the rssi values
    print(doodle1.get_channel_frequency_width())