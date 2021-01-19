import logging
import random
from pyraftlib.states import State
from pyraftlib.workers.thread_worker import ThreadWorker
from pyraftlib.events import NoopEvent, TerminateEvent
from pyraftlib.raft_pb2 import (RequestVoteResponse, AppendEntriesResponse,
        RequestVoteRequest, AppendEntriesRequest)

logger = logging.getLogger(__name__)


class Follower(State):
    Display = 'Follower'
    def __init__(self, name=None, stale_state=None, service=None):
        super().__init__(name=name, stale_state=stale_state, service=service)
        self.log.set_vote_for(None)
        self.timer = ThreadWorker(on_event=self.on_timer_event, on_timeout=self.on_timer_timerout,
                get_timeout=self.get_timer_timeout)
        self.timer.start()

    def refresh_timer(self):
        self.timer.submit(NoopEvent())

    def on_timer_event(self, event):
        return True, None

    def get_timer_timeout(self):
        return random.randint(4,8) * random.randint(8,10) ** -1

    def on_timer_timerout(self):
        from pyraftlib.states.candidate import Candidate
        reason = f'{self.Display} {self.name} Timeout. Converted to Candidate'
        logger.info(reason)
        self.service.convert_to(Candidate)
        return False, reason

    def on_peer_append_entries(self, request):
        current_term = self.log.get_current_term()
        active_term = request.term >= current_term

        response = AppendEntriesResponse()
        response.peer_id = self.name
        response.term = current_term
        response.request_term = request.term
        if not active_term:
            logger.info(f'{self.name} current_term {current_term} received {request.peer_id} with stale term {request.term}. Ignore')
            response.success = False
            return response

        prev_entry = self.log.get_entry(request.prevLogIndex)
        # logger.info(f'prevLogIndex {request.prevLogIndex} prev_entry {prev_entry}')

        if not prev_entry and request.prevLogIndex == 1:
            response.success = True
        elif not prev_entry or prev_entry.term != request.prevLogTerm:
            response.success = False
            return response

        response.term = request.term
        if request.term > current_term:
            self.log.set_current_term(request.term)
            self.log.set_vote_for(0)
            self.volatile_state.leader_id = request.peer_id

        if not self.volatile_state.leader_id:
            self.volatile_state.leader_id = request.leaderId
        else:
            assert self.volatile_state.leader_id == request.leaderId, f'current_leader={self.volatile_state.leader_id}, request.leader={request.leaderId}'
        self.log.log_entries(request.entries)
        response.last_log_index = self.log.last_log_entry().index
        self.refresh_timer()
        response.success = True
        return response

    def on_peer_vote_response(self, response):
        logger.error(f'>>> Should not be called!')
        return True, None

    def on_peer_vote_request(self, request):
        current_term = self.log.get_current_term()
        active_term = request.term >= current_term
        can_vote = self.log.get_vote_for() in (request.peer_id, None) or request.term > current_term

        last_entry = self.log.last_log_entry()
        log_ok = False
        if last_entry.term < request.lastLogTerm or (last_entry.term == request.lastLogTerm and last_entry.index <= request.lastLogIndex):
            log_ok = True

        granted = active_term and can_vote and log_ok

        if granted:
            self.log.set_vote_for(request.peer_id)
            self.refresh_timer()

        logger.info(f'{self.Display} {self.name} voting for {request.candidateId}. Term:{current_term} Active:{active_term} CanVote:{can_vote} Granted:{granted}')
        response = RequestVoteResponse()
        response.term = current_term
        response.voteGranted = granted
        response.peer_id = self.name
        return response

    def shutdown(self):
        self.timer.submit(TerminateEvent())

    def __del__(self):
        self.shutdown()
        # logger.info(f'{self.Display} {self.name} is down')
