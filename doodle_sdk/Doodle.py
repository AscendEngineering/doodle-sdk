import requests
import json
import re
import warnings
import time
from typing import Dict

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
            time.sleep(0.5)

        return False

    def _gen_login_payload(self, user: str, password: str) -> Dict[str, str]:

        login_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "call",
            "params": ["00000000000000000000000000000000", "session", "login", {"username": user, "password": password}]
        }
        
        return login_payload