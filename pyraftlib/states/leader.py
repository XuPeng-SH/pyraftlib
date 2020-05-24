import logging
import time

from pyraftlib.states import State
from pyraftlib.raft_pb2 import (RequestVoteRequest, AppendEntriesRequest,
        RequestVoteResponse, AppendEntriesResponse)
from pyraftlib.workers.thread_worker import ThreadWorker
from pyraftlib.events import TerminateEvent, DelayEvent
from pyraftlib.states.follower import Follower

logger = logging.getLogger(__name__)

class Leader(State):
    def __init__(self, name=None, stale_state=None, service=None):
        super().__init__(name=name, stale_state=stale_state, service=service)
        self.timer = ThreadWorker(on_event=self.on_timer_event, on_timeout=self.on_timer_timerout,
                get_timeout=self.get_timer_timeout)
        self.timer.start()

    def get_timer_timeout(self):
        return 2* 12 ** -1

    def send_append_entries(self):
        request = AppendEntriesRequest()
        request.term = self.persist_state.current_term
        request.leaderId = self.name
        request.peer_id = self.name
        self.service.send_append_entries(request)

    def on_timer_timerout(self):
        self.send_append_entries()
        return True, None

    def on_timer_event(self, event):
        if isinstance(event, DelayEvent):
            time.sleep(event.delay)
        return True, None

    def on_peer_vote_response(self, event):
        return True, None

    def on_peer_vote_request(self, request):
        active_term = request.term > self.persist_state.current_term
        if active_term:
            self.service.convert_to(Follower)
            return self.service.on_peer_vote_request(request)

        response = RequestVoteResponse()
        response.term = self.persist_state.current_term
        response.voteGranted = False
        response.peer_id = self.name
        return response

    def on_peer_append_entries_event(self, event):
        active_term = event.term > self.persist_state.current_term
        if not active_term:
            logger.info(f'Leader {self.name} received from {event.leaderId} with stale term. Ignore')
            return True, None

        logger.info(f'Leader {self.name} received from {event.leaderId}. Will convert to Follower')
        self.service.convert_to(Follower)
        self.on_peer_append_entries_event(event)
        return True, None

    def shutdown(self):
        self.timer.submit(TerminateEvent())
        # self.timer.join()

    def __del__(self):
        self.shutdown()
        logger.info(f'Leader {self.name} is down')
