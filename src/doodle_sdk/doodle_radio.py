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
                response = self._session.post(self._url, json=login_payload, verify=False, timeout=1)
                data = response.json()

                # Extract the token
                self._token = data['result'][1]['ubus_rpc_session']
                return True
            except:
                pass

        return False

    def get_associated_list(self):
        """Retrieves the list of associated stations from the Doodle.
    
        Returns:
            dict: A dictionary containing the translated response from the Doodle of associated stations.
        Raises:
            TypeError: If the Doodle is not connected (missing token or URL).
            requests.exceptions.RequestException: If there is an issue with the HTTP request.
        """
        if not self._token or not self._url:
            raise TypeError("Must connect to the Doodle before requesting its associated stations")

        assoclist_payload = self._gen_assoclist_payload(self._token)
        response = self._session.post(self._url, json=assoclist_payload, verify=False, timeout=1)
        stats_response = stats.translate_stat_response(response.json())
        
        return stats_response

    def get_channel_frequency_width(self):
        """Retrieves the channel, frequency, and channel width from the Doodle device.

        Raises:
            TypeError: If the device is not connected (i.e., `_token` or `_url` is not set).

        Returns:
            tuple: A tuple containing the channel, frequency, and channel width.
        """
        if not self._token or not self._url:
            raise TypeError("Must connect to the Doodle before requesting its associated stations")

        channel_frequency_payload = self._gen_channel_frequency_payload(self._token)
        response = self._session.post(self._url, json=channel_frequency_payload, verify=False, timeout=1)
        self.channel, self.frequency, self.channel_width = settings.translate_channel_frequency_response(response.json())

        return self.channel, self.frequency, self.channel_width

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
            "params": ["00000000000000000000000000000000", "session", "login", {"username": user, "password": password}]
        }
        
        return login_payload