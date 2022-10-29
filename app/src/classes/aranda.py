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
    
    def __init__(self, config: dict, renew_auth_interval: int = 1200, timeout: float = 60) -> None:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.__renew_auth_interval = renew_auth_interval
        self.__timeout = timeout
        (self.__token, self.__renew_token) = (None, None)
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
                custom_log(f'[AUTH] Attempting to renew authentication', 'yellow')
                try:
                    start = time.perf_counter()
                    response = requests.post(
                        self.__cfg['base_url'] + self.__cfg['api']['re_auth']['res_path'], 
                        headers=self.__headers, 
                        json = self.__renew_token, 
                        timeout=self.__timeout, 
                        verify = False
                        )
                except Exception as e:
                    custom_log(f'[AUTH] Failed to reauthenticate - {e}', 'red')
                    custom_log(f'[AUTH] Attempting to reauthenticate immediately', 'yellow')
            else:
                custom_log(f'[AUTH] Attempting to authenticate', 'yellow')
                try:
                    start = time.perf_counter()
                    response = requests.post(
                        self.__cfg['base_url'] + self.__cfg['api']['auth']['res_path'], 
                        headers=self.__headers, 
                        json = self.__auth_payload, 
                        timeout=self.__timeout, 
                        verify = False
                        )
                except Exception as e:
                    custom_log(f'[AUTH] Failed to authenticate - {e}', 'red')
                    custom_log(f'[AUTH] Attempting to authenticate immediately', 'yellow')
            if response.status_code >= 200 and response.status_code < 300:
                try:
                    self.__token, self.__renew_token =  response.json()['token'], response.json()['renewToken']
                    custom_log(f'[AUTH] Authentication successs - status code {response.status_code}', 'yellow')
                    custom_log(f'[AUTH] Aranda response time in seconds: {int(time.perf_counter()-start)}', 'yellow')
                except Exception as e:
                    custom_log(f'[AUTH] Failed to authenticate - status code {response.status_code} - no token found in Aranda response', 'red')
                    custom_log(f'[AUTH] Aranda response time in seconds: {int(time.perf_counter()-start)}', 'yellow')
                    self.__token, self.__renew_token = None, None
                    custom_log(f'[AUTH] Attempting to reauthenticate immediately', 'yellow')
                    sc.enter(0, 1, self._auth_request, (sc,))
            else:
                custom_log(f'[AUTH] Failed to authenticate - status code {response.status_code}', 'red')
                custom_log(f'[AUTH] Aranda response time in seconds: {int(time.perf_counter()-start)}', 'yellow')
                self.__token, self.__renew_token = None, None
                custom_log(f'[AUTH] Attempting to reauthenticate immediately', 'yellow')
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

    def __request_header(self):
        header = self.__headers
        token = self.__token
        if token:
            header['X-Authorization'] = 'Bearer ' + token
            header['UrlAsms'] = self.__cfg['base_url']
            header['TokenAsms'] = token
            return header
        else:
            return None

    def request(
        self, 
        obj_type: str, 
        query: str = None, 
        payload: dict = None, 
        method: str = 'get', 
        ret_path: str = None, 
        retries: int = 3, 
        timeout: float = None) -> dict:

        self.__retries = retries if retries else self.__retries
        self.__timeout = timeout if timeout else self.__timeout
        for i in range(self.__retries):
            header = self.__request_header()
            
            if not header:
                if (i + 1) >= self.__retries:
                    custom_log(f'[ERROR] ({i}) Could not get token on last attempt', 'red')
                    return None
                else:
                    custom_log(f'[WARN] ({i}) Could not get token', 'yellow')
                    continue
            
            request_method = {
                'get': requests.get,
                'post': requests.post,
                'put': requests.put,
                'delete': requests.delete
            }
            start = 0

            try:
                custom_log(f'[INFO] ({i}) Calling token validation', 'green')
                start = time.perf_counter()
                if payload:
                    response = request_method[method](
                        url = self.__cfg['base_url'] + self.__cfg['api'][obj_type]['res_path'] + pn(query), 
                        headers = header, 
                        json = payload, 
                        verify = False,
                        timeout = self.__timeout
                    )
                else:
                    response = request_method[method](
                        url = self.__cfg['base_url'] + self.__cfg['api'][obj_type]['res_path'] + pn(query), 
                        headers = header, 
                        verify = False,
                        timeout = self.__timeout
                    )
                elapsed_time = int(time.perf_counter()-start)
                if (elapsed_time < 10):
                    custom_log(f'[INFO] Aranda response time in seconds: {elapsed_time}', 'green')
                if (elapsed_time >= 10):
                    custom_log(f'[WARN] Aranda response time in seconds: {elapsed_time}', 'yellow')
                if response.status_code >= 200 and response.status_code < 300:
                    custom_log(f'[INFO] Status code {response.status_code}', 'green')
                else:
                    custom_log(f'[ERROR] Status code {response.status_code}', 'red')
                    if "You do not have permission to view this directory or page." in response.text:
                        custom_log(f'[ERROR] Someone got the token', 'red')
                        continue
                if self.__cfg["app"]["log_level"] == "info":
                    custom_log(f'[INFO] Response text {response.text}', 'green')
            except Exception as e:
                raise
            return response

