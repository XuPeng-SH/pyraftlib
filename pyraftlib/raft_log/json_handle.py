import sys, os
import logging
import json
import threading
from google.protobuf.internal.encoder import _VarintBytes
from google.protobuf.internal.decoder import _DecodeVarint32
from pyraftlib.raft_log import LogFactory, BaseLog
from pyraftlib.raft_pb2 import LogEntry

logger = logging.getLogger(__name__)

RAFT_LOG_DIR_NAME = 'rlog'
RAFT_LOG_META_NAME_TEMPLATE = 'meta-peer-{}.json'
RAFT_LOG_DATA_NAME_TEMPLATE = 'data-peer-{}.json'

class DataCache:
    def __init__(self, capacity=-1):
        assert (capacity >= 1 or capacity == -1), f'Invalid DataCache capacity: {capacity}'
        self.capacity = capacity
        self.cache = []
        self.lock = threading.RLock()
        self.mutation_lock = threading.Lock()
        self.dirty = []
        self.in_mutation = False

    @property
    def first_index(self):
        with self.lock:
            if len(self.cache) == 0:
                return 0
            return self.cache[0].index

    @property
    def last_entry(self):
        with self.lock:
            if len(self.cache) == 0:
                empty_entry = LogEntry()
                empty_entry.index = 0
                empty_entry.term = 0
                return empty_entry
            return self.cache[-1]

    def insert(self, entry):
        if not self.in_mutation:
            with self.lock:
                if self.capacity != -1 and len(self.cache) >= self.capacity:
                    del(self.cache[0])
                    self.cache.append(entry)
                    return

                self.cache.append(entry)
            return


    def start_mutation(self):
        self.mutation_lock.acquire()
        self.dirty = []

    def abort_mutation(self):
        self.dirty = []
        self.mutation_lock.release()

    def insert_mutation(self, entry):
        assert self.mutation_lock.locked()
        self.dirty.append(entry)

    def commit_mutation(self):
        assert self.mutation_lock.locked()
        if len(self.dirty) == 0:
            return True

        with self.lock:
            if self.dirty[0].index != self.last_entry.index + 1:
                return False
            self.cache.extend(self.dirty)
            if self.capacity != -1 and len(self.cache) > self.capacity:
                self.cache = self.cache[len(self.cache) - self.capacity:]

        self.mutation_lock.release()
        return True


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
        self.meta_log = os.path.join(self.raft_log_dir, RAFT_LOG_META_NAME_TEMPLATE.format(peer_id))
        self.meta_values = dict(current_term=0, vote_for=0, last_log_index=0)
        if os.path.exists(self.meta_log):
            with open(self.meta_log, 'r') as f:
                self.meta_values = json.load(f)
        else:
            with open(self.meta_log, 'w') as f:
                json.dump(self.meta_values, f)

        self.data_log = os.path.join(self.raft_log_dir, RAFT_LOG_DATA_NAME_TEMPLATE.format(peer_id))
        self.data_values_cache = DataCache(capacity=50)
        self.pos_index = []
        self.last_pos = 0

        lines = []
        if os.path.exists(self.data_log):
            lines = self.load_last_n_entries(update=True)

        if len(lines) >= self.data_values_cache.capacity:
            start_pos = len(lines) - self.data_values_cache.capacity
            lines = lines[start_pos:]

        for entry in lines:
            self.data_values_cache.insert(entry)

        self.lock = threading.RLock()
        self.data_lock = threading.RLock()

    def load_last_n_entries(self, n=None, update=False):
        entries = []
        with open(self.data_log, 'rb') as f:
            buf = f.read()
            pos = 0
            while pos < len(buf):
                # self.pos_index[len(entries) + 1] = pos
                update and self.pos_index.append(pos)
                msg_len, new_pos = _DecodeVarint32(buf, pos)
                pos = new_pos
                msg_buf = buf[pos:pos+msg_len]
                pos += msg_len
                entry = LogEntry()
                entry.ParseFromString(msg_buf)
                entries.append(entry)
            if update:
                self.last_pos = len(buf)
                self.pos_index.append(pos)
        if n is None or n >= len(entries):
            return entries
        return entries[len(entries)-n:]

    def load_entries(self, from_index=None, to_index=None, max_size=None):
        if from_index is None:
            from_index = 1
        if to_index is None:
            to_index = self.last_log_entry().index
        if from_index < to_index:
            return []
        last_pos = self.pos_index[from_index-1]
        accm = 0
        poses = []
        # steps = []
        for pos in self.pos_index[from_index:to_index+1]:
            step = pos - last_pos
            # steps.append(step)
            accm += step
            last_pos = pos
            if max_size is not None and accm >= max_size:
                break

        with open(self.data_log, 'rb') as f:
            f.seek(self.pos_index(from_index -1))
            buf = f.read(accm)
            pos = 0
            while pos < len(buf):
                msg_len, new_pos = _DecodeVarint32(buf, pos)
                pos = new_pos
                msg_buf = buf[pos:pos+msg_len]
                pos += msg_len
                entry = LogEntry()
                entry.ParseFromString(msg_buf)
                entries.append(entry)


        # with open(self.data_log, 'rb') as f:


    def _update(self, **kwargs):
        with self.lock:
            self.meta_values.update(**kwargs)
            with open(self.meta_log, 'w') as f:
                json.dump(self.meta_values, f)

    def get_current_term(self):
        with self.lock:
            return self.meta_values.get('current_term')

    def set_current_term(self, term):
        self._update(current_term=term)

    def last_log_entry(self):
        return self.data_values_cache.last_entry

    def get_vote_for(self):
        with self.lock:
            return self.meta_values.get('vote_for')

    def set_vote_for(self, vote_for):
        self._update(vote_for=vote_for)

    def log_entries(self, entries):
        if len(entries) == 0:
            return True
        with self.data_lock:
            to_dump = bytes()
            self.data_values_cache.start_mutation()
            last_index = self.data_values_cache.last_entry.index
            extra_pos = []
            for i, entry in enumerate(entries):
                if entry.index != last_index + i + 1:
                    logger.error(f'Entry {entry.index} should be consestive from last_index {last_index + i + 1}')
                    self.data_values_cache.abort_mutation()
                    return False
                self.data_values_cache.insert_mutation(entry)
                extra_pos.append(self.last_pos + len(to_dump))
                to_dump += _VarintBytes(entry.ByteSize()) + entry.SerializeToString()
            try:
                with open(self.data_log, 'ab') as f:
                    f.write(to_dump)
            except Exception as exp:
                logger.error(f'Errors found during log_entries to {self.data_log}: {exp}')
                self.data_values_cache.abort_mutation()
                return False

            self.data_values_cache.commit_mutation()
            self.last_pos += len(to_dump)
            self.pos_index.extend(extra_pos)
            # logger.info(f'last_pos = {self.last_pos} length of pos_index = {len(self.pos_index)} extra_pos = {extra_pos}')

            return True

    def get_entry(self, index):
        entries = self.get_entries(index, 1)
        if len(entries) == 0:
            return None
        assert len(entries) == 1, f'len of entries is {len(entries)}'
        return entries[0]

    def get_entries(self, from_index=None, count=None, batch_size=-1):
        ret = []
        if count == 0 or batch_size == 0:
            return ret
        with self.data_lock:
            last_entry = self.last_log_entry()
            if from_index > last_entry.index:
                return []
            c_l_i = self.data_values_cache.first_index

            if from_index < c_l_i:
                logger.info(f'get_entries from_index={from_index} last_entry_index={last_entry.index}')
                entries = self.load_last_n_entries(last_entry.index - from_index + 1)
                if count:
                    entries = entries[0:count]
                return entries
            else:
                to_index = last_entry.index + 1
                if count is not None:
                    to_index = min(to_index, from_index + count)

                return self.data_values_cache.cache[(from_index - c_l_i):(to_index - c_l_i)]


    def truncate_entries(self, from_index):
        if from_index == 0:
            return True
        with self.data_lock:
            last_entry = self.last_log_entry()
            if from_index > last_entry.index:
                return

            pos = self.pos_index[from_index - 1]

            try:
                with open(self.data_log, 'wb') as f:
                    f.truncate(pos)
            except Exception as exp:
                logger.error(f'truncate_entries from index {from_index} error: {exp}')
                return False

            self.last_pos = self.pos_index[pos]
            self.pos_index = self.pos_index[:from_index - 1]

        return True
