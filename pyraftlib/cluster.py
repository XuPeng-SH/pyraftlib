import logging
import threading

# from pyraftlib.workers.thread_worker import ThreadWorker
from pyraftlib.rpc_client import RpcClient
from pyraftlib.raft_pb2 import AppendEntriesResponse, RequestVoteResponse

logger = logging.getLogger(__name__)

class Cluster(object):
    def __init__(self, peer_id, peers, state=None):
        self.lock = threading.Lock()
        self.peers = peers
        self.peer_id = peer_id
        self.active_peers = {}
        self.state = state

    def process_future_callback(self, future):
        response = future.result()
        logger.info(f'Response [{response.__class__.__name__}] from {response.peer_id}')
        # if isinstance(response, AppendEntriesResponse):
        #     self.state.on_peer_append_entries_event(response)
        # elif isinstance(response, RequestVoteResponse):
        #     self.state.on_peer_vote_request_event(response)

        # raise RuntimeError(f'Unkown response [{response.__class__.__name__}]')

    def on_peer_connected_event(self, event):
        logger.info(f'Cluster PeerConnectedEvent: {event.peer_id}')

        with self.lock:
            if event.peer_id not in self.active_peers:
                peer_info = self.peers[event.peer_id]
                host = peer_info.split(':')[0]
                port = peer_info.split(':')[1]
                self.active_peers[event.peer_id] = RpcClient(host=host, port=port,
                        done_cb=self.process_future_callback)
        return True, None

    def on_peer_vote_request_event(self, event):
        clients = {}
        with self.lock:
            for peer_id, client in self.active_peers.items():
                clients[peer_id] = client
        for peer_id, client in clients.items():
            client.RequestVote(event.request, sync=False)
        return True, None

    def shutdown(self):
        pass
        # self.response_processor.submit(TerminateEvent())

    def __del__(self):
        self.shutdown()
