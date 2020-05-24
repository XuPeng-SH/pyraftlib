import logging
import random
from pyraftlib.states import State
from pyraftlib.workers.thread_worker import ThreadWorker
from pyraftlib.events import NoopEvent, TerminateEvent

logger = logging.getLogger(__name__)

class Follower(State):
    def __init__(self, name=None, stale_state=None, service=None):
        super().__init__(name=name, stale_state=stale_state, service=service)
        self.persist_state.voted_for = None
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
        reason = f'{self.name} FollowerTimeout. Converted to Candidate'
        logger.info(reason)

        return False, reason

    def on_peer_append_entries_event(self, event):
        current_term = self.persist_state.current_term
        active_term = event.term >= current_term
        if not active_term:
            logger.info(f'{self.name} current_term {current_term} received {event.peer_id} with stale term {event.term}. Ignore')
            return True, None

        self.persist_state.current_term = event.term
        self.volatile_state.leader_id = event.peer_id
        self.refresh_timer()
        return True, None

    def on_peer_vote_request_event(self, event):
        current_term = self.persist_state.current_term
        active_term = event.term >= current_term
        can_vote = self.persist_state.voted_for in (event.peer_id, None) or event.term > current_term
        granted = active_term and can_vote

        if granted:
            self.persist_state.voted_for = event.peer_id
            self.refresh_timer()

        logger.debug(f'{self.name} voting for {event.peer_id}. Active:{active_term} CanVote:{can_vote} Granted:{granted}')
        # response_event =

    def shutdown(self):
        self.timer.submit(TerminateEvent())
        self.timer.join()
        logger.info(f'Follower {self.name} timer is down')

    def __del__(self):
        self.shutdown()
