import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('/home/xupeng/github/pyraftlib/pyraftlib')

import logging
import threading
import fire
from pyraftlib.service import Service

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(message)s (%(filename)s:%(lineno)d)')

def Run(yaml_path):
    service = Service(yaml_path)
    def send_entries(s):
        import time
        time.sleep(2)
        i = 0
        while True:
            try:
                s.log_entries(f'MESSGE-({i})')
                i += 1
                time.sleep(0.5)
            except Exception as exp:
                logger.error(exp)
                break

    send_f = threading.Thread(target=send_entries, args=(service,))
    send_f.start()

    service.run()
    send_f.join()

if __name__ == '__main__':
    fire.Fire(Run)
