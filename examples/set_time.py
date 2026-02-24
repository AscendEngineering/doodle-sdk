from doodle_sdk.doodle_radio import Doodle

if __name__ == '__main__':

    # Connect to radio
    doodle = Doodle(ip="10.223.82.95", user="user", password="DoodleSmartRadio")
    doodle.connect()

    # # Set the radio's time to the current host time
    # success = doodle.set_time()
    # print("Set time to host time:", "Success" if success else "Failed")

    # Or set to a specific Unix timestamp
    success = doodle.set_time(1771970641)
    print("Set time to specific timestamp:", "Success" if success else "Failed")

    # #revert to current 
    success = doodle.set_time()
    print("Set time to host time:", "Success" if success else "Failed")
