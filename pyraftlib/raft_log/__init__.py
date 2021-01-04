class LogFactory(object):
    __HANDLERS__ = {}

    @classmethod
    def register_handler(cls, handler_class):
        handle_name = getattr(handler_class, 'HANDLE_NAME', None)
        assert handle_name
        cls.__HANDLERS__[handle_name] = handler_class
        return handler_class

    @classmethod
    def build(cls, conf, **kwargs):
        log_handle_conf = conf.get('log_handle', {})
        assert log_handle_conf, f'"log_handle" not found in conf'
        name = log_handle_conf.get('name')
        log_handle_class = cls.__HANDLERS__.get(name)
        assert log_handle_class, f'Specified log handle "{name}" not found'
        log_handle = log_handle_class.build(log_handle_conf, **kwargs)
        return log_handle


class BaseLog(object):
    def get_current_term(self):
        raise NotImplemented()

    def set_current_term(self, term):
        raise NotImplemented()

    def get_last_log_index(self):
        raise NotImplemented

    def set_last_log_index(self, index):
        raise NotImplemented

    def get_vote_for(self):
        raise NotImplemented()

    def set_vote_for(self, vote_for):
        raise NotImplemented

from pyraftlib.raft_log.mock_handle import MockHandle
from pyraftlib.raft_log.json_handle import JsonHandle
