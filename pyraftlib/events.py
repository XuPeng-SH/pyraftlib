
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
