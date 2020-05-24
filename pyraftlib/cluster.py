import logging
import threading

# from pyraftlib.workers.thread_worker import ThreadWorker
from pyraftlib.rpc_client import RpcClient
from pyraftlib.raft_pb2 import (AppendEntriesResponse, RequestVoteResponse,
        AppendEntriesRequest, RequestVoteRequest)

logger = logging.getLogger(__name__)

class Cluster(object):
    def __init__(self, peer_info, peers, service):
        self.lock = threading.Lock()
        self.peers = peers
        self.peer_info = peer_info
        self.active_peers = {}
        self.service = service
        for peer_id, peer in self.peers.items():
            self.active_peers[peer_id] = RpcClient(host=peer['host'], port=peer['port'],
                    done_cb=self.process_future_callback)

    def on_process_response_exception(self, client, exc):
        logger.error(f'Client [{client.host}:{client.port}] Encounter Exception: {type(exc)}')

    def process_future_callback(self, client, future):
        try:
            response = future.result()
        except Exception as exc:
            self.on_process_response_exception(client, exc)
            return
        logger.info(f'Response [{response.__class__.__name__}] from {response.peer_id}')

        if response.__class__.__name__ == AppendEntriesResponse.__name__:
            self.service.on_peer_append_entries_response(response)
        elif response.__class__.__name__ == RequestVoteResponse.__name__:
            self.service.on_peer_vote_response(response)
        # elif isinstance(response, RequestVoteResponse):
        #     self.state.on_peer_vote_request_event(response)

        # raise RuntimeError(f'Unkown response [{response.__class__.__name__}]')

    def send_append_entries(self, request):
        clients = {}
        with self.lock:
            for peer_id, client in self.active_peers.items():
                clients[peer_id] = client
        for peer_id, client in clients.items():
            client.AppendEntries(request, sync=False)
        for peer_id, client in self.active_peers.items():
            client.AppendEntries(request, sync=False)

    def send_vote_requests(self, request):
        for peer_id, client in self.active_peers.items():
            client.RequestVote(request, sync=False)

    def on_peer_vote_request(self, request):
        return self.service.on_peer_vote_request(request)

    def shutdown(self):
        pass

    def __del__(self):
        self.shutdown()
