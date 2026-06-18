from doodle_sdk.doodle_radio import Doodle
import time

if __name__ == '__main__':

    # No IP needed: auto_connect finds the interface on the 10.223.0.0/16
    # subnet, derives the radio's IP from its MAC, and logs in.
    doodle = Doodle(user="root", password="DoodleSmartRadio")
    doodle.auto_connect()

    print(f"Connected to radio at {doodle._ip}")

    while True:
        associated_list = doodle.get_associated_list()
        for station in associated_list:
            print(f"{station.mac}: noise {station.noise}, signal {station.signal}")
        time.sleep(1)
