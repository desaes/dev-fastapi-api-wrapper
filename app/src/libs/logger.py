from termcolor import colored
from datetime import datetime
import sys

def custom_log(msg: str, color: str = 'red') -> None:
    print(colored(f'{datetime.now()} - {msg}', color), file=sys.stderr)
    sys.stderr.flush()