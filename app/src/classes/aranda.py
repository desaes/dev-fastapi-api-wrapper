import os
import requests
import sched
import time
import threading
import urllib3
from src.libs.logger import custom_log
from src.libs.utils import print_nothing as pn
import time

class Aranda():
    
    def __init__(self, config: dict, renew_auth_interval: int = 1200, timeout: float = 120) -> None:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.__renew_auth_interval = renew_auth_interval
        self.__timeout = timeout
        (self.__sc, self.__token, self.__renew_token) = (0, None, None)
        self.__s = sched.scheduler(time.time, time.sleep)
        self.__lock = threading.RLock()
        self.__cfg = config
        self.__headers = {
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'Content-Type': 'application/json'
        }
        self.__auth_payload = {
            'userName': os.getenv('ARANDA_USER'),
            'password': os.getenv('ARANDA_PASS'),
            'consoleType': self.__cfg['auth_data']['console_type'],
            'providerId': self.__cfg['auth_data']['provider_id']
        }
        self.auth()

    def __bool__(self):
        return bool(self.__token)

    def __repr__(self) -> str:
        pass

    def _auth_request(self, sc) -> None:
        with self.__lock:
            start = 0
            if self.__renew_token:
                custom_log(f'AUTH:     Attempting to renew authentication', 'yellow')
                try:
                    start = time.perf_counter()
                    response = requests.post(self.__cfg['base_url'] + self.__cfg['api']['re_auth']['res_path'], headers=self.__headers, json = self.__renew_token, timeout=self.__timeout, verify = False)
                except Exception as e:
                    raise
            else:
                custom_log(f'AUTH:     Attempting to authenticate', 'yellow')
                try:
                    start = time.perf_counter()
                    response = requests.post(self.__cfg['base_url'] + self.__cfg['api']['auth']['res_path'], headers=self.__headers, json = self.__auth_payload, timeout=self.__timeout, verify = False)
                except Exception as e:
                    raise

            self.__sc = response.status_code
            if self.__sc == 200:
                custom_log(f'AUTH:     Authentication successs - status code {self.__sc}', 'yellow')
                custom_log(f'AUTH:     Aranda response time in seconds: {int(time.perf_counter()-start)}', 'yellow')
                self.__token, self.__renew_token =  response.json()['token'], response.json()['renewToken']
            else:
                custom_log(f'AUTH:     Failed to authenticate - status code {self.__sc}', 'red')
                custom_log(f'AUTH:     Aranda response time in seconds: {int(time.perf_counter()-start)}', 'red')
                self.__token, self.__renew_token = None, None
                custom_log(f'AUTH:     Attempting to reauthenticate immediately', 'yellow')
                sc.enter(0, 1, self._auth_request, (sc,))
        sc.enter(self.__renew_auth_interval, 1, self._auth_request, (sc,))

    def _auth(self):
        self.__s.enter(0, 1, self._auth_request, (self.__s,))
        self.__s.run()

    def auth(self):
        self.__task = threading.Thread(target=self._auth)
        self.__task.daemon = True
        self.__task.start()

    def token(self) -> str:
        with self.__lock:
            return self.__token