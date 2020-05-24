import logging
import queue
import threading
from raft_service.events import TerminateEvent

logger = logging.getLogger(__name__)


class ThreadWorker(threading.Thread):
    def __init__(self, *args, **kwargs):
        qsize = kwargs.pop('qsize', 0)
        on_event = kwargs.pop('on_event', None)
        self.on_event = on_event if on_event and callable(on_event) else self.on_event

        on_timeout = kwargs.pop('on_timeout', None)
        self.on_timeout = on_timeout if on_timeout and callable(on_timeout) else self.on_timeout

        get_timeout = kwargs.pop('get_timeout', None)
        self.get_timeout = get_timeout if get_timeout and callable(get_timeout) else self.get_timeout

        super().__init__(*args, **kwargs)
        self.lock = threading.Lock()
        self.queue = queue.Queue(maxsize=qsize)

    def submit(self, event):
        with self.lock:
            self.queue.put_nowait(event)

    def stop(self):
        self.submit(TerminateEvent())

    def on_event(self, event):
        return True, None

    def get_timeout(self):
        return None

    def on_timeout(self):
        logger.error(f'{self} on_event: timeout')
        return True, None

    def run(self):
        ret, reason = True, None
        while True:
            timeout = self.get_timeout()
            try:
                event = self.queue.get(timeout=timeout)
            except queue.Empty as exc:
                ret, reason = self.on_timeout()
                event = None

            if ret and isinstance(event, TerminateEvent):
                reason = 'TerminateEvent'
                break

            if ret:
                ret, reason = self.on_event(event)

            if not ret:
                break

        # logger.debug(f'Terminated: {reason}')
