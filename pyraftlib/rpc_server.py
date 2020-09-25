import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import threading
import grpc
from grpc._cython import cygrpc
from concurrent import futures
from pyraftlib.raft_pb2_grpc import add_RaftServiceServicer_to_server
from pyraftlib.rpc_handler import RpcHandler
from pyraftlib.cluster import Cluster

logger = logging.getLogger(__name__)


class RpcServer:
    def __init__(self, peer_info, peers, service, **kwargs):
        self.service = service
        self.peers = peers
        self.peer_info = peer_info
        server_cacert = kwargs.get('server_cacert', None)
        server_private_key = kwargs.get('server_private_key', None)
        client_cacert = kwargs.get('client_cacert', None)

        self.cluster = Cluster(self.peer_info, self.peers, service, client_cacert=client_cacert)

        self.add_port_args = [f'[::]:{self.peer_info["port"]}']

        self.server_credentials = None

        if server_cacert and server_private_key:
            with open(server_cacert, 'rb') as f:
                cacert = f.read()
            with open(server_private_key, 'rb') as f:
                private_key = f.read()

            self.server_credentials = grpc.ssl_server_credentials(((private_key, cacert,),))
            self.add_port_args.append(self.server_credentials)

        self.max_workers = kwargs.get('max_workers', 10)

        self.server_impl = grpc.server(
            thread_pool=futures.ThreadPoolExecutor(max_workers=self.max_workers),
            options=[(cygrpc.ChannelArgKey.max_send_message_length, -1),
                     (cygrpc.ChannelArgKey.max_receive_message_length, -1)]
        )

        self.add_port_method = self.server_impl.add_secure_port if self.server_credentials \
                else self.server_impl.add_insecure_port

    def dump(self):
        header = f'---------------------Raft Service Info Start------------------'
        logger.info(header)
        cluster_info_1 = f'Cluster of {len(self.peers) + 1} Peers'
        logger.info(cluster_info_1)
        self_peer_info = f'\tPeerId={self.peer_info["peer_id"]}, PeerHost={self.peer_info["host"]}, PeerPort={self.peer_info["port"]}'
        logger.info(self_peer_info)
        for pid, peer in self.peers.items():
            peer_info = f'\tPeerId={pid}, PeerHost={peer["host"]}, PeerPort={peer["port"]}'
            logger.info(peer_info)
        logger.info(f'This server\'s PeerId is \"{self.peer_info["peer_id"]}\"')
        tail = f'---------------------Raft Service Info  End------------------'
        logger.info(tail)

    def start(self, *args, **kwargs):
        self.dump()
        handler = RpcHandler(cluster=self.cluster, service=self.service)
        add_RaftServiceServicer_to_server(handler, self.server_impl)
        self.add_port_method(*self.add_port_args)
        logger.info(f'RpcServer is listening on port {self.peer_info["port"]}')
        self.server_impl.start()

    def stop(self):
        self.server_impl.stop(0)
        logger.info(f'RpcServer is down now')
