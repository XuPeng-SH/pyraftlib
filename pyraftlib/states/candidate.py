import logging
import time

from pyraftlib.states.follower import Follower
from pyraftlib.events import VoteRequestEvent
from pyraftlib.raft_pb2 import (RequestVoteRequest, RequestVoteResponse,
        AppendEntriesRequest, AppendEntriesResponse)
from pyraftlib.events import TerminateEvent
from pyraftlib.states.leader import Leader

logger = logging.getLogger(__name__)

class Candidate(Follower):
    Display = 'Candidate'
    def __init__(self, name=None, stale_state=None, service=None):
        super().__init__(name=name, stale_state=stale_state, service=service)
        self.persist_state.current_term += 1
        self.votes_count = 1
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

    def on_peer_append_entries(self, request):
        current_term = self.persist_state.current_term
        active_term = request.term >= current_term
        response = AppendEntriesResponse()
        response.peer_id = self.name
        # response.term = self.term
        response.term = current_term
        response.request_term = request.term
        if not active_term:
            logger.info(f'Candidate {self.name} recieved AE from {request.leaderId} with stale term. Ignore')
            response.success = False
            return response

        logger.info(f'Candidate {self.name} recieved AE from {request.leaderId}. Will convert to Follower')
        self.service.convert_to(Follower)
        return self.service.on_peer_append_entries(request)

    def on_peer_vote_response(self, response):
        self.service.set_last_resp_ts(response.peer_id, time.time())
        self.votes_count += 1 if response.voteGranted else 0
        logger.info(f'{self.Display} {self.name} has vote count: {self.votes_count}')
        if self.votes_count > (len(self.service.peers) + 1) / 2:
            logger.info(f'{self.Display} {self.name} win the election! Converted to Leader')
            self.service.convert_to(Leader)
        return True, None
