import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import threading
import grpc
from grpc._cython import cygrpc
from concurrent import futures
from pyraftlib.raft_pb2_grpc import add_RaftServiceServicer_to_server
from pyraftlib import raft_pb2_grpc, raft_pb2
from pyraftlib.rpc_handler import RpcHandler
from pyraftlib.cluster import Cluster

logger = logging.getLogger(__name__)


class RpcServer:
    def __init__(self, peer_id, peers):
        self.lock = threading.Lock()
        self.terminate_cv = threading.Condition(self.lock)
        self.terminated = False
        self.peers = peers
        self_peer = self.peers.pop(peer_id)
        self.peer_id = peer_id
        self.host = self_peer.split(':')[0]
        self.port = self_peer.split(':')[1]
        self.cluster = Cluster(self.peer_id, self.peers)

    def init_app(self, *args, **kwargs):
        self.max_workers = kwargs.get('max_workers', 10)

        self.server_impl = grpc.server(
            thread_pool=futures.ThreadPoolExecutor(max_workers=self.max_workers),
            options=[(cygrpc.ChannelArgKey.max_send_message_length, -1),
                     (cygrpc.ChannelArgKey.max_receive_message_length, -1)]
        )

    def dump(self):
        header = f'---------------------Raft Service Info Start------------------'
        logger.info(header)
        cluster_info_1 = f'Cluster of {len(self.peers) + 1} Peers'
        logger.info(cluster_info_1)
        self_peer_info = f'\tPeerId={self.peer_id}, PeerHost={self.host}, PeerPort={self.port}'
        logger.info(self_peer_info)
        for pid, peer in self.peers.items():
            host = peer.split(':')[0]
            port = peer.split(':')[1]
            peer_info = f'\tPeerId={pid}, PeerHost={host}, PeerPort={port}'
            logger.info(peer_info)
        logger.info(f'This server\'s PeerId is \"{self.peer_id}\"')
        tail = f'---------------------Raft Service Info  End------------------'
        logger.info(tail)

    def start(self, *args, **kwargs):
        self.dump()
        handler = RpcHandler(cluster=self.cluster)
        add_RaftServiceServicer_to_server(handler, self.server_impl)
        self.server_impl.add_insecure_port(f'[::]:{self.port}')
        logger.info(f'RpcServer is listening on port {self.port}')
        self.server_impl.start()

    def stop(self):
        with self.lock:
            self.server_impl.stop(0)
            self.terminated = True
            self.terminate_cv.notify_all()

    def run(self):
        self.start()
        try:
            with self.lock:
                self.terminate_cv.wait()
        except KeyboardInterrupt:
            self.stop()

        logger.info(f'Server is down now')

if __name__ == '__main__':
    import time
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(message)s (%(filename)s:%(lineno)d)')

    def mock_client(s):
        import time
        time.sleep(1)
        from pyraftlib.rpc_client import RpcClient
        client_handler = RpcClient(done_cb=s.cluster.process_future_callback)
        request = raft_pb2.AppendEntriesRequest()
        request.term = 111
        client_handler.AppendEntries(request, sync=False)

        request = raft_pb2.RequestVoteRequest()
        request.term = 222
        client_handler.RequestVote(request, sync=False)

        time.sleep(1)
        logger.info(f'Client is stopping server')
        s.stop()

    server = RpcServer(1, {
        1: 'localhost:18888',
        2: 'localhost:18898',
        3: 'localhost:18808'
    })
    server.init_app()

    client = threading.Thread(target=mock_client, args=(server, ))
    client.start()

    server.run()
    client.join()
