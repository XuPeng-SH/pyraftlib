import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('/home/xupeng/github/pyraftlib/pyraftlib')

import logging
import fire
from pyraftlib.service import Service

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(message)s (%(filename)s:%(lineno)d)')

def Run(yaml_path):
    service = Service(yaml_path)
    service.run()

if __name__ == '__main__':
    fire.Fire(Run)
