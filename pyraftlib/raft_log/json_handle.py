import sys, os
import json
import threading
from pyraftlib.raft_log import LogFactory, BaseLog

RAFT_LOG_DIR_NAME = 'rlog'
RAFT_LOG_META_NAME_TEMPLATE = 'meta-peer-{}.json'

@LogFactory.register_handler
class JsonHandle(BaseLog):
    HANDLE_NAME = 'JsonHandle'

    @classmethod
    def build(cls, conf, **kwargs):
        assert conf['name'] == cls.HANDLE_NAME
        return cls(conf, **kwargs)

    def __init__(self, conf, **kwargs):
        self.dir_root = conf.get('dir_root')
        if not self.dir_root:
            self.dir_root = os.path.dirname(os.path.abspath(sys.argv[0]))

        self.raft_log_dir = os.path.join(self.dir_root, RAFT_LOG_DIR_NAME)
        if not os.path.exists(self.raft_log_dir):
            os.makedirs(self.raft_log_dir)

        peer_id = kwargs.get('peer_id')
        assert peer_id is not None, 'peer_id is required building JsonHandle'
        self.raft_meta_log = os.path.join(self.raft_log_dir, RAFT_LOG_META_NAME_TEMPLATE.format(peer_id))
        self.values = dict(current_term=0, vote_for=0, last_log_index=0)
        if os.path.exists(self.raft_meta_log):
            with open(self.raft_meta_log, 'r') as f:
                self.values = json.load(f)
        else:
            with open(self.raft_meta_log, 'w') as f:
                json.dump(self.values, f)

        self.lock = threading.Lock()

    def _update(self, **kwargs):
        with self.lock:
            self.values.update(**kwargs)
            with open(self.raft_meta_log, 'w') as f:
                json.dump(self.values, f)

    def get_current_term(self):
        with self.lock:
            return self.values.get('current_term')

    def set_current_term(self, term):
        self._update(current_term=term)

    def get_last_log_index(self):
        with self.lock:
            return self.values.get('last_log_index')

    def set_last_log_index(self, index):
        self._update(last_log_index=index)

    def get_vote_for(self):
        with self.lock:
            return self.values.get('vote_for')

    def set_vote_for(self, vote_for):
        self._update(vote_for=vote_for)
