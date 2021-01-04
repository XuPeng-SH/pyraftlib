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
    Display = 'Leader'
    def __init__(self, name=None, stale_state=None, service=None):
        super().__init__(name=name, stale_state=stale_state, service=service)
        self.timer = ThreadWorker(on_event=self.on_timer_event, on_timeout=self.on_timer_timerout,
                get_timeout=self.get_timer_timeout)
        self.timer.start()

    def get_timer_timeout(self):
        return 3* 12 ** -1

    def send_append_entries(self):
        request = AppendEntriesRequest()
        request.term = self.log.get_current_term()
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
        active_term = request.term > self.log.get_current_term
        if active_term:
            logger.info(f'{self} will convert to follower: current_term={self.log.get_current_term()} request.term={request.term}')
            self.service.convert_to(Follower)
            return self.service.on_peer_vote_request(request)

        response = RequestVoteResponse()
        response.term = self.log.get_current_term()
        response.voteGranted = False
        response.peer_id = self.name
        return response

    def run_loop_func(self):
        self._handle_leader_timeout()

    def _handle_leader_timeout(self):
        tss = [time.time()]
        for peer_id, peer in self.service.peers.items():
            last_resp_ts = peer.get('last_resp_ts', 0)
            tss.append(last_resp_ts)

        tss = sorted(tss, reverse=True)
        elapsed = time.time() - tss[len(tss) >> 1]
        #TODO
        max_timeout = 8 * 8 ** -1
        if elapsed >= max_timeout:
            logger.info(f'{self} will convert to follower: elapsed time {elapsed} passed')
            self.service.convert_to(Follower)

    def on_peer_append_entries(self, request):
        active_term = request.term > self.log.get_current_term()
        response = AppendEntriesResponse()
        response.peer_id = self.name
        response.term = request.term
        if not active_term:
            logger.debug(f'{self.Display} {self.name} received from {request.leaderId} with stale term. Ignore')
            response.success = False
            return response

        logger.debug(f'{self.Display} {self.name} received from {request.leaderId}. Will convert to Follower')
        self.service.convert_to(Follower)
        return self.on_peer_append_entries(event)

    def on_peer_append_entries_response(self, response):
        self.service.set_last_resp_ts(response.peer_id, time.time())
        current_term, to_skip = super().on_peer_append_entries_response(response)
        if to_skip:
            return current_term, False

        if current_term < response.term:
            self.service.convert_to(Follower)
            self.log.set_current_term(response.term)
            self.log.set_vote_for(None)
            self.volatile_state.leader_id = None

        # TODO:
        logger.info(f'{self} Recieving AE Response: term={response.term} success={response.success} peer_id={response.peer_id}')

        return response.term, True

    def shutdown(self):
        self.timer.submit(TerminateEvent())
        # self.timer.join()

    def __del__(self):
        self.shutdown()
        logger.info(f'{self.Display} {self.name} is down')
