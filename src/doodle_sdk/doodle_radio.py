import requests
import json
import re
import warnings
import time
from typing import Dict
from . import stats
from . import settings


class Doodle:

    def __init__(self, ip: str = None, user: str = None, password: str = None):
        """Creates an instance of the Doodle class

        Args:
            ip: IP address of the Doodle
            user: username of the Doodle
            password: password of the Doodle

        Returns:
            Instance of Doodle class

        Raises:
            None
        """
        
        self._ip = ip
        self._user = user
        self._password = password
        self._url = None
        self._token = None

        # Radio Settings
        self._channel = None
        self._frequency = None
        self._channel_width = None

        # Disable warnings for self-signed certificates
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
        self._session = requests.Session()

    def connect(self, ip: str = None, user: str = None, password: str = None) -> bool:
        """Connects to the Doodle and attempts to get the rpc session token

        Args:
            ip: IP address of the Doodle (required to connect)
            user: username of the Doodle
            password: password of the Doodle

        Returns:
            True if connection is successful, False if not

        Raises:
            TypeError: If the IP address of the Doodle was never set
        """

        if ip: 
            self._ip = ip
        elif (not self._ip):
            raise TypeError("Must set an IP address before connecting")

        self._url = f'https://{self._ip}/ubus'

        # keep the defaults if they never specified a user / password
        if user:
            self._user = user
        elif (not self._user):
            warnings.warn("No username specified, defaulting to \"user\"")
            self._user = "user"

        if password:
            self._password = password
        elif (not self._password):
            warnings.warn("No password specified, defaulting to \"DoodleSmartRadio\"")
            self._password = "DoodleSmartRadio"

        login_payload = self._gen_login_payload(self._user, self._password)

        for attempt in range(5): # Attempts to connect to the Doodle 5 times
            try:
                response = self._session.post(self._url, json=login_payload, verify=False)
                data = response.json()

                # Extract the token
                self._token = data['result'][1]['ubus_rpc_session']
                return True
            except:
                pass

        return False
        

    def get_associated_list(self):
        if not self._token or not self._url:
            raise TypeError("Must connect to the Doodle before requesting its associated stations")

        assoclist_payload = self._gen_assoclist_payload(self._token)
        response = self._session.post(self._url, json=assoclist_payload, verify=False, timeout=1)
        
        if response.status_code != 200:
            response = self.retry(response, assoclist_payload, 1)
        
        stats_response = stats.translate_stat_response(response.json())
        
        return stats_response

    def get_channel_info(self):

        if not self._token or not self._url:
            raise TypeError("Must connect to the Doodle before requesting its frequency, channel, and width")

        channel_frequency_payload = self._gen_channel_frequency_payload(self._token)
        response = self._session.post(self._url, json=channel_frequency_payload, verify=False, timeout=1)
        
        if response.status_code != 200:
            response = self._retry(response, channel_frequency_payload, 10)
        
        if response.status_code != 200:
            return None

        self.channel, self.channel_width = settings.translate_channel_frequency_response(response.json())
        return self.channel, self.channel_width

    def get_frequency(self):

        if not self._token or not self._url:
            raise TypeError("Must connect to the Doodle before requesting its frequency, channel, and width")


        fes_model_payload = self._gen_fes_model_payload(self._token)

        response = self._session.post(self._url, json=fes_model_payload, verify=False)
        data = response.json()

        # Process the result
        if 'result' in data and len(data['result']) > 1:
            stdout = data['result'][1].get('stdout', '')
            output = stdout.strip()
        else:
            print("No result found or error in execution")


        if output == "RM-2455-2KM-XW":
            self._frequency = 2455
        elif output == "RM-2450-2KM-XW":
            self._frequency = 2450
        elif output == "RM-915-2KM-XW":
            self._frequency = 915
        else: 
            raise Exception("Did not read the frequency succesfully")

        return self._frequency
        

    def set_frequency(self, frequency: int):

        if not self._token or not self._url:
            raise TypeError("Must connect to the Doodle before setting its frequency")

        self.get_channel_info()

        band_switching_payload = self._gen_set_freq_channel_bandwidth_payload(self._token, frequency, self._channel, self._channel_width)
        response = self._session.post(self._url, json=band_switching_payload, verify=False, timeout=10)

        if response.status_code != 200:
            response = self._retry(response, band_switching_payload, 10)
        
        return True if response.status_code != 200 else False

    def set_channel(self, ch: int):

        if not self._token or not self._url:
            raise TypeError("Must connect to the Doodle before setting its channel")

        self.get_channel_info()
        self.get_frequency()

        band_switching_payload = self._gen_set_freq_channel_bandwidth_payload(self._token, self._frequency, ch, self._channel_width)
        response = self._session.post(self._url, json=band_switching_payload, verify=False, timeout=10)

        print(response.json())

        if response.status_code != 200:
            response = self._retry(response, band_switching_payload, 10)
        
        return True if response.status_code != 200 else False

    def set_channel_width(self, channel_width: int):

        if not self._token or not self._url:
            raise TypeError("Must connect to the Doodle before setting its channel")

        self.get_channel_info()
        self.get_frequency()

        band_switching_payload = self._gen_set_freq_channel_bandwidth_payload(self._token, self._frequency, self._channel, channel_width)
        response = self._session.post(self._url, json=band_switching_payload, verify=False, timeout=10)

        if response.status_code != 200:
            response = self._retry(response, band_switching_payload, 10)
        
        return True if response.status_code != 200 else False

    def _retry(self, response, payload, timeout):
        for retry in range(5):
            self.connect()
            response = self._session.post(self._url, json=payload, verify=False, timeout=timeout)

            if (response.status == 200):
                break

            time.sleep(1)

        return response

    def _gen_channel_frequency_payload(self, token: str):

        channel_frequency_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "call",
            "params": [token, "file", "exec", {"command": "iw", "params": ["wlan0", "info"]}]
        }
        return channel_frequency_payload

    def _gen_assoclist_payload(self, token: str):

        assoclist_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "call",
            "params": [token, "iwinfo", "assoclist", {
                "device": "wlan0"
            }]
        }

        return assoclist_payload

    def _gen_login_payload(self, user: str, password: str) -> Dict[str, str]:

        login_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "call",
            "params": ["00000000000000000000000000000000", "session", "login", {"username": self._user, "password": self._password}]
        }
        return login_payload

    def _gen_fes_model_payload(self, token: str):
        fes_model_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "call",
            "params": [token, "file", "exec", {
                "command": "fes_model.sh",
                "params": ["get"]
            }]
        }

        return fes_model_payload


    def _gen_set_freq_channel_bandwidth_payload(self, token: str, frequency: int, channel: int, channel_width: int):

        if (frequency == 2455):
            submodel = "RM-2455-2KM-XW"
        elif (frequency == 2450):
            submodel = "RM-2450-2KM-XW"
        elif (frequency == 915):
            submodel = "RM-915-2KM-XW"
        else:
            raise ValueError("Frequency should be one of either 2455, 2450, or 915 MHz")

        band_switching_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "call",
            "params": [token, "file", "exec", {
                "command": "/usr/share/simpleconfig/band_switching.sh",
                "params": [submodel, "{channel}", "{channel_width}"]
            }]
        }

        return band_switching_payload