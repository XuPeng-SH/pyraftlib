import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import fire
from pyraftlib.raft_log import JsonHandle

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(message)s (%(filename)s:%(lineno)d)')

h = JsonHandle({'dir_root': '.'}, peer_id=2)
# h = JsonHandle({'dir_root': '/home/xupeng/github/pyraftlib/examples/'}, peer_id=2)
logger.info(h.last_log_entry().index)
logger.info(h.last_log_entry().term)
logger.info(h.last_log_entry().entry)

entries = h.load_last_n_entries(10)
logger.info(len(entries))
logger.info(f'{entries[0].index}   {entries[-1].index}')

# entries = h.load_entries(from_index=10, to_index=20)
# logger.info(len(entries))
# logger.info(f'{entries[0].index}   {entries[-1].index}')

# entries = h.load_entries(from_index=10, max_size=100)
# logger.info(len(entries))
# logger.info(f'{entries[0].index}   {entries[-1].index}')

entry = h.get_entry(0)
logger.info(f'{entry.index}   {entry.term}')
