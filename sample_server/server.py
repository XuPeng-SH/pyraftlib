import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('/home/xupeng/github/pyraftlib/pyraftlib')

import logging
import threading
import time
import queue

from pyraftlib.service import Service as RaftService

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(message)s (%(filename)s:%(lineno)d)')

class Server:
    def __init__(self, yaml_path=None):
        self.yaml_path = yaml_path
        # self.raft_service = RaftService(...)
        self.queue = queue.Queue(1000)
        self.receive_loop = threading.Thread(target=self.receive_loop)
        self.raft_loop = threading.Thread(target=self.run_raft_loop)
        self.stop = False

    def receive_loop(self):
        while not self.stop:
            try:
                event = self.queue.get(timeout=1)
                logger.info(f'get event {event}')
            except queue.Empty:
                continue
        logger.info(f'Receive meesage loop exited!')

    def run_raft_loop(self):
        while not self.stop:
            pass
            # time.sleep(0.5)
            # logger.info(f'run_raft_loop ...')

        logger.info(f'Raft loop exited!')

    def submit(self, event):
        self.queue.put_nowait(event)

    def run(self):
        logger.info(f'Start receive message loop ...')
        self.receive_loop.start()
        logger.info(f'Start raft loop ...')
        self.raft_loop.start()

    def terminate(self):
        self.stop = True
        self.raft_loop.join()
        self.receive_loop.join()

if __name__ == '__main__':
    class Event:
        def __init__(self, eid, message=""):
            self.eid = eid
            self.message = message

    s = Server()
    def feature_stop(server, sec):
        time.sleep(sec)
        server.terminate()

    stop_f = threading.Thread(target=feature_stop, args=(s, 5))
    stop_f.start()

    def send_message(server):
        time.sleep(1)
        for i in range(5):
            server.submit(Event(i, f'message-{i}'))
            time.sleep(0.5)

    send_m = threading.Thread(target=send_message, args=(s,))
    send_m.start()

    s.run()
    send_m.join()
    stop_f.join()
