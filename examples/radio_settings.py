from doodle_sdk.doodle_radio import Doodle
import doodle_sdk.stats as stats
import time

if __name__ == '__main__':

    # Connect to radio
    doodle1 = Doodle(ip="10.223.97.204", user="user", password="DoodleSmartRadio")
    doodle1_connected = doodle1.connect()

    # # Get the rssi values
    doodle1.get_channel_info()
    doodle1.get_frequency()

    print("Frequency:", doodle1._frequency)

    print('------------------------')

    # Set the frequency, channel, bandwidth
    doodle1.set_frequency(915)

    # Get the rssi values
    doodle1.get_channel_info()
    doodle1.get_frequency()

    print("Frequency:", doodle1._frequency)
