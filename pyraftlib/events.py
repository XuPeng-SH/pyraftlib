import threading

class NoopEvent:
    pass

class TerminateEvent:
    pass

class DelayEvent:
    def __init__(self, delay):
        self.delay = delay

# class RaftEvent:
#     def __init__(self, term, source=None, destination=None):
#         self.term = term
#         self.source = source
#         self.destination = destination

# class VoteRequestEvent(RaftEvent):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)

class BaseEvent:
    def __init__(self, *args, **kwargs):
        self.mutex = threading.Lock()
        self.error = None
        self.err_message = ''
        self.has_done = threading.Condition(self.mutex)
        self.done = False

    def result(self, timeout=None):
        with self.has_done:
            if self.done:
                return self
            self.has_done.wait(timeout=timeout)

    def pre_set_done(self, **kwargs):
        pass

    def mark_done(self, error=None, err_message='', **kwargs):
        with self.has_done:
            if self.done:
                raise RuntimeError(f'mark_done on already done event')
            self.done = True
            self.error = error
            self.err_message = err_message
            self.pre_set_done(**kwargs)
            self.has_done.notify()

class LogEntryEvent(BaseEvent):
    def __init__(self, entry, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entry = entry

class AppendEntriesRequestEvent(BaseEvent):
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.response = None

    def pre_set_done(self, **kwargs):
        assert self.response is not None, f'response should be set before mark {self.__class__.__name__} done'

class RequestVoteRequestEvent(BaseEvent):
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.response = None

    def pre_set_done(self, **kwargs):
        assert self.response is not None, f'response should be set before mark {self.__class__.__name__} done'

class LogEntriesEvent(BaseEvent):
    def __init__(self, entries, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entries = entries
