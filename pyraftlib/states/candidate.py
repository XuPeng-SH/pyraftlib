import logging

from pyraftlib.states.follower import Follower
from pyraftlib.events import VoteRequestEvent
from pyraftlib.raft_pb2 import RequestVoteRequest
from pyraftlib.events import TerminateEvent

logger = logging.getLogger(__name__)

class Candidate(Follower):
    def __init__(self, name=None, stale_state=None, service=None):
        super().__init__(name=name, stale_state=stale_state, service=service)
        self.persist_state.current_term += 1
        self.votes_count = 0
        logger.info(f'Candidate {self.name} Start New Election. Term: {self.persist_state.current_term}')
        self.send_vote_requests()

    def send_vote_requests(self):
        logger.info(f'Candidate {self.name} is Broadcasting RequestVote')
        self.persist_state.voted_for = self.name
        event = VoteRequestEvent(term=self.persist_state.current_term,
                                 source=self.name)
        request = RequestVoteRequest()
        request.term = self.persist_state.current_term
        request.candidateId = self.name
        request.peer_id = self.name
        self.service.send_vote_requests(request)

    def on_timer_timerout(self):
        logger.info(f'Candidate {self.name} start election from timeout')
        return True, None

    def on_peer_append_entries_event(self, event):
        active_term = event.term >= self.persist_state.current_term
        if not active_term:
            logger.info(f'Candidate {self.name} recieved AE from {event.peer_id} with stale term. Ignore')
            return True, None

        logger.info(f'Candidate {self.name} recieved AE from {event.peer_id}. Will convert to Follower')
        self.service.convert_to(Follower)
        self.service.on_peer_append_entries_event(event)
        return True, None

    def on_peer_vote_response_event(self, event):
        self.votes_count += 1 if event.granted else 0
        logger.info(f'Candidate {self.name} vote count: {self.votes_count}')
        if self.votes_count > (len(self.service.peers) + 1) / 2:
            logger.info(f'Candidate {self.name} win the election! Converted to Leader')
            self.service.convert_to(Leader)
        return True, None

    def shutdown(self):
        self.timer.submit(TerminateEvent())

    def __del__(self):
        self.shutdown()
        logger.info(f'Candidate {self.name} is down')
