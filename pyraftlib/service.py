import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import yaml
import threading
from collections import defaultdict

from pyraftlib.rpc_server import RpcServer
from pyraftlib.states.follower import Follower

logger = logging.getLogger(__name__)

def parse_conf_peers(peers):
    info = {}
    peers = peers.split(',')
    for peer in peers:
        peer = peer.strip()
        if not peer:
            continue
        peer_id, peer_info = peer.split('@')
        host, port = peer_info.split(':')
        info[int(peer_id)] = dict(host=host, port=port)
    return info

class Service:
    def __init__(self, yaml_path=None, conf=None):
        assert yaml_path or conf
        self.yaml_path = yaml_path
        self.conf = {} if not self.yaml_path else self.load_conf_from_yaml_path(yaml_path)
        conf and self.conf.update(conf)
        peer_id = self.conf['cluster']['peer_id']
        peers = parse_conf_peers(self.conf['cluster']['peers'])
        self.peer_info = peers.pop(peer_id)
        self.peer_info['peer_id'] = peer_id
        self.peers = peers
        self.rpc_server = RpcServer(peer_info=self.peer_info, peers=self.peers)
        self.cluster = self.rpc_server.cluster
        self.state = None
        self.lock = threading.Lock()
        self.terminate_cv = threading.Condition(self.lock)
        self.terminated = False

    def load_conf_from_yaml_path(self, yaml_path):
        with open(yaml_path, 'r') as f:
            conf = yaml.load(f, Loader=yaml.FullLoader)
        return conf

    def start(self):
        self.rpc_server.start()
        self.state = Follower(name=self.peer_info['peer_id'], service=service)

    def run(self):
        self.start()
        try:
            with self.lock:
                self.terminate_cv.wait()
        except KeyboardInterrupt:
            self.stop()

        logger.info(f'Service is down now')

    def stop(self):
        with self.lock:
            self.rpc_server.stop()
            self.terminated = True
            self.terminate_cv.notify_all()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(message)s (%(filename)s:%(lineno)d)')
    service = Service('../examples/example.yml')
    def mock_client(s):
        import time
        time.sleep(1)
        from pyraftlib.rpc_client import RpcClient
        from pyraftlib import raft_pb2_grpc, raft_pb2
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

    client = threading.Thread(target=mock_client, args=(service, ))
    client.start()

    service.run()
    client.join()
