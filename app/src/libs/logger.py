from termcolor import colored
import datetime
import time
import sys
import os

def custom_log(msg: str, color: str = 'red') -> None:
    print(colored(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ")}{time.strftime("%z")}] [{os.getpid()}] {msg}', color), file=sys.stderr)
    sys.stderr.flush()