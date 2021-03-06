from pyraftlib.raft_log import LogFactory, BaseLog

@LogFactory.register_handler
class MockHandle(BaseLog):
    HANDLE_NAME = 'MockHandle'

    @classmethod
    def build(cls, conf, **kwargs):
        assert conf['name'] == cls.HANDLE_NAME
        return cls(conf)

    def __init__(self, conf):
        self.current_term = 0
        self.vote_for = 0
        # self.prev_log_index = 0
        self.prev_log_entry = None

    def get_current_term(self):
        return self.current_term

    def set_current_term(self, term):
        self.current_term = term

    def last_log_entry(self):
        return self.prev_log_entry

    # def set_last_log_index(self, index):
    #     self.last_log_index = index

    def get_vote_for(self):
        return self.vote_for

    def set_vote_for(self, vote_for):
        self.vote_for = vote_for

    def get_entries(self, from_index=None, count=None):
        return []
