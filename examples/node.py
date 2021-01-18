import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('/home/xupeng/github/pyraftlib/pyraftlib')

import logging
import threading
import fire
from pyraftlib.service import Service
from pyraftlib.raft_pb2 import LogEntry
from pyraftlib.events import LogEntryEvent

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
                entry = LogEntry()
                entry.term = 100
                entry.index = i
                entry.entry = str.encode(f'hello-{i}')
                event = LogEntryEvent(entry)
                s.log_entries_async([event])
                event.result()
                if not event.error:
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
    # import time
    # from pyraftlib.events import LogEntryEvent
    # e1 = LogEntryEvent(f'111111111')
    # e2 = LogEntryEvent(f'222222222')
    # def process_f(event, delay):
    #     logger.info(f'received event {event.entry}')
    #     time.sleep(delay)
    #     logger.info(f'processing event {event.entry}')
    #     event.mark_done()

    # f1 = threading.Thread(target=process_f, args=(e1, 2))
    # f2 = threading.Thread(target=process_f, args=(e2, 1))
    # f1.start()
    # f2.start()

    # def show_result(event, timeout=None):
    #     event.result(timeout=timeout)
    #     logger.info(f'done event {event.entry}')

    # s1 = threading.Thread(target=show_result, args=(e1,))
    # s2 = threading.Thread(target=show_result, args=(e2,))
    # s1.start()
    # s2.start()

    # f1.join()
    # f2.join()
    # s1.join()
    # s2.join()

    fire.Fire(Run)
