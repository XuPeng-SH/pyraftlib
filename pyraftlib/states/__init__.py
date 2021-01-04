import logging
import time
from collections import defaultdict

logger = logging.getLogger(__name__)

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class VolatileState:
    def __init__(self, commit_index=0, last_applied_index=0, leader_id=None, leader_state=None):
        self.commit_index = commit_index
        self.last_applied_index = last_applied_index
        self.leader_id = leader_id
        self.leader_state = leader_state if leader_state else LeaderVolatileState()


class LeaderVolatileState:
    def __init__(self):
        self.next_index = defaultdict(int)
        self.match_index = defaultdict(int)


class PersistState:
    def __init__(self, current_term=0, voted_for=None):
        self.current_term = current_term
        self.voted_for = voted_for


class State:
    def __init__(self, name=None, stale_state=None, service=None):
        self.name = name
        self.service = service
        if stale_state:
            self.inherit_from_stale(stale_state)
        else:
            self.init()

    def inherit_from_stale(self, stale_state):
        self.name = stale_state.name
        self.service = stale_state.service
        self.volatile_state = stale_state.volatile_state
        self.persist_state = stale_state.persist_state

    def init(self):
        assert self.name is not None
        self.volatile_state = VolatileState(0, 0)
        self.persist_state = PersistState()

    def run_loop_func(self):
        time.sleep(0.5)

    def on_peer_append_entries_response(self, response):
        current_term = self.persist_state.current_term
        if response.request_term != current_term:
            logger.warning(f'Received AE Resp of term {response.request_term} while current_term is {current_term}. Skip it')
            return current_term, False
        return current_term, True

    def __str__(self):
        return f'[{self.Display}:{self.name}]'

    __repr__ = __str__
