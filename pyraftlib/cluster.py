import logging
import threading

from pyraftlib.rpc_client import RpcClient
from pyraftlib.raft_pb2 import (AppendEntriesResponse, RequestVoteResponse,
        AppendEntriesRequest, RequestVoteRequest)

logger = logging.getLogger(__name__)

class Cluster(object):
    def __init__(self, self_peer, peers, service, **kwargs):
        self.lock = threading.Lock()
        self.peers = peers
        self.self_peer = self_peer
        self.active_peers = {}
        self.service = service
        for peer_id, peer in self.peers.items():
            self.active_peers[peer_id] = RpcClient(host=peer.host, port=peer.port,
                    done_cb=self.process_future_callback, service=self.service, **kwargs)

    def on_process_response_exception(self, client, exc):
        # logger.error(f'Client [{client.host}:{client.port}] Encounter Exception: {type(exc)}')
        pass

    def process_future_callback(self, client, future):
        try:
            response = future.result()
        except Exception as exc:
            self.on_process_response_exception(client, exc)
            return
        # logger.info(f'Response [{response.__class__.__name__}] from {response.peer_id}')

        if hasattr(response, 'success'):
            return self.service.on_peer_append_entries_response(response)
        elif hasattr(response, 'voteGranted'):
            return self.service.on_peer_vote_response(response)

        raise RuntimeError(f'Unkown response [{response.__class__}]')

    def send_append_entries(self, requests):
        for peer_id, client in self.active_peers.items():
            client.AppendEntries(requests[peer_id], sync=False)

    def send_vote_requests(self, request):
        for peer_id, client in self.active_peers.items():
            client.RequestVote(request, sync=False)

    def on_peer_vote_request(self, request):
        return self.service.on_peer_vote_request(request)

    def on_peer_append_entries(self, request):
        return self.service.on_peer_append_entries(request)

    def shutdown(self):
        pass

    def __del__(self):
        self.shutdown()
