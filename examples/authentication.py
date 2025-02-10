from doodle_sdk.doodle_radio import Doodle

if __name__ == '__main__':

    # Option 1: Specify the ip address / username / password in the constructor
    doodle1 = Doodle(ip="10.223.108.26", user="root", password="DoodleSmartRadio")
    doodle1_connected = doodle1.connect()
    print(doodle1_connected) 

    # Option 2: Specify the ip address / username / password in the connect function
    doodle2 = Doodle()
    doodle2_connected = doodle2.connect(ip="10.223.108.26", user="root", password="DoodleSmartRadio")
    print(doodle2_connected)

    # Option 3: Don't specify the username or password: default username, password is "user", "DoodleSmartRadio"
    doodle3 = Doodle(ip="10.223.108.26")
    doodle3_connected = doodle3.connect()
    print(doodle3_connected)

    doodle4 = Doodle()
    print(doodle4.connect())
    

