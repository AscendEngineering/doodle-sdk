from doodle_sdk.doodle_radio import Doodle
import doodle_sdk.stats as stats
import time

if __name__ == '__main__':

    # Connect to radio
    doodle1 = Doodle(ip="10.223.108.26", user="root", password="DoodleSmartRadio")
    doodle1_connected = doodle1.connect()
    print(doodle1_connected) 

    # Get the rssi values
    start_time = time.time()
    while (True):
        associated_list = doodle1.get_associated_list()
        print(associated_list)
        for station in associated_list:
            print(f"{station.mac}: noise {station.noise}, signal {station.signal}")
        time.sleep(1)
        print("time ", time.time() - start_time)
    # print(associated_list)