import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import time
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
        secure_config = self.conf.get('security', {})
        self.loop_running = True
        self.raft_loop = threading.Thread(target=self.do_raft_loop)
        self.rpc_server = RpcServer(peer_info=self.peer_info, peers=self.peers, service=self, **secure_config)
        self.cluster = self.rpc_server.cluster
        self.state = None
        self.lock = threading.Lock()
        self.terminate_cv = threading.Condition(self.lock)
        self.terminated = False

    def load_conf_from_yaml_path(self, yaml_path):
        with open(yaml_path, 'r') as f:
            conf = yaml.load(f, Loader=yaml.FullLoader)
        return conf

    def set_last_resp_ts(self, peer_id, ts):
        peer = self.peers.get(peer_id, None)
        if not peer:
            logger.error(f'Specified peer {peer_id} not found!')
            return False

        peer['last_resp_ts'] = ts
        # logger.info(f'Set peer_id={peer_id} last_resp_ts={ts}')
        return True

    def convert_to(self, state_type):
        self.state.shutdown()
        logger.info(f'>>> State {type(self.state).__name__} Converted To {state_type.__name__} ')
        self.state = state_type(stale_state=self.state)

    def start(self):
        self.rpc_server.start()
        self.state = Follower(name=self.peer_info['peer_id'], service=self)
        self.raft_loop.start()

    def do_raft_loop(self):
        while self.loop_running:
            self.state.run_loop_func()

        logger.info(f'raft_loop exited')

    def stop_raft_loop(self):
        self.loop_running = False
        self.raft_loop.join()

    def run(self):
        self.start()
        try:
            with self.lock:
                self.terminate_cv.wait()
        except KeyboardInterrupt:
            self.stop()

        logger.info(f'Service is down now')

    def stop(self):
        self.stop_raft_loop()
        with self.lock:
            self.rpc_server.stop()
            self.terminated = True
            self.terminate_cv.notify_all()
        if self.state:
            self.state.shutdown()

    def send_append_entries(self, request):
        self.cluster.send_append_entries(request)

    def send_vote_requests(self, event):
        self.cluster.send_vote_requests(event)

    def on_peer_append_entries_response(self, response):
        self.state.on_peer_append_entries_response(response)

    def on_peer_vote_response(self, response):
        self.state.on_peer_vote_response(response)

    def on_peer_vote_request(self, request):
        return self.state.on_peer_vote_request(request)

    def on_peer_append_entries(self, request):
        return self.state.on_peer_append_entries(request)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(message)s (%(filename)s:%(lineno)d)')
    service = Service('../examples/example.yml')
    def mock_client(s):
        import time
        time.sleep(0.8)
        from pyraftlib.rpc_client import RpcClient
        from pyraftlib import raft_pb2_grpc, raft_pb2
        client_handler = RpcClient(done_cb=s.cluster.process_future_callback)
        # request = raft_pb2.AppendEntriesRequest()
        # request.term = 111
        # client_handler.AppendEntries(request, sync=False)

        request = raft_pb2.RequestVoteRequest()
        request.term = 222
        client_handler.RequestVote(request, sync=False)

        time.sleep(0.8)
        logger.info(f'Client is stopping server')
        s.stop()

    client = threading.Thread(target=mock_client, args=(service, ))
    client.start()

    service.run()
    client.join()
