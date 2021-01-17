import threading

class NoopEvent:
    pass

class TerminateEvent:
    pass

class DelayEvent:
    def __init__(self, delay):
        self.delay = delay

class RaftEvent:
    def __init__(self, term, source=None, destination=None):
        self.term = term
        self.source = source
        self.destination = destination

class VoteRequestEvent(RaftEvent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class VoteResponseEvent(RaftEvent):
    def __init__(self, granted, **kwargs):
        self.granted = kwargs.pop('granted')
        super().__init__(**kwargs)

class LogEntryEvent:
    def __init__(self, entry):
        self.mutex = threading.Lock()
        self.entry = entry
        self.error = None
        self.err_message = ''
        self.has_done = threading.Condition(self.mutex)
        self.done = False

    def result(self, timeout=None):
        with self.has_done:
            if self.done:
                return self
            self.has_done.wait(timeout=timeout)

    def mark_done(self, error=None, err_message=''):
        with self.has_done:
            if self.done:
                raise RuntimeError(f'mark_done on already done event')
            self.done = True
            self.error = error
            self.err_message = err_message
            self.has_done.notify()
