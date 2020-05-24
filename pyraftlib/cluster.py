import logging
import threading

# from pyraftlib.workers.thread_worker import ThreadWorker
from pyraftlib.rpc_client import RpcClient
from pyraftlib.raft_pb2 import AppendEntriesResponse, RequestVoteResponse

logger = logging.getLogger(__name__)

class Cluster(object):
    def __init__(self, peer_info, peers, service):
        self.lock = threading.Lock()
        self.peers = peers
        self.peer_info = peer_info
        self.active_peers = {}
        self.service = service

    def process_future_callback(self, future):
        response = future.result()
        logger.info(f'Response [{response.__class__.__name__}] from {response.peer_id}')

        if response.__class__.__name__ == AppendEntriesResponse.__name__:
            self.service.on_peer_append_entries_response(response)
        # elif isinstance(response, RequestVoteResponse):
        #     self.state.on_peer_vote_request_event(response)

        # raise RuntimeError(f'Unkown response [{response.__class__.__name__}]')

    def on_peer_connected_event(self, event):
        logger.info(f'Cluster PeerConnectedEvent: {event.peer_info}')

        with self.lock:
            if event.peer_id not in self.active_peers:
                peer_info = self.peers[event.peer_id]
                host = peer_info.split(':')[0]
                port = peer_info.split(':')[1]
                self.active_peers[event.peer_id] = RpcClient(host=host, port=port,
                        done_cb=self.process_future_callback)
        return True, None

    def send_append_entries(self, request):
        clients = {}
        with self.lock:
            for peer_id, client in self.active_peers.items():
                clients[peer_id] = client
        for peer_id, client in clients.items():
            client.AppendEntries(request, sync=False)

    def send_vote_requests(self, request):
        clients = {}
        with self.lock:
            for peer_id, client in self.active_peers.items():
                clients[peer_id] = client
        for peer_id, client in clients.items():
            client.RequestVote(request, sync=False)


    def shutdown(self):
        pass

    def __del__(self):
        self.shutdown()
