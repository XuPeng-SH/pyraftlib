import logging
import grpc
from functools import partial

from pyraftlib import raft_pb2_grpc, raft_pb2

logger = logging.getLogger(__name__)


class RpcClient:
    def __init__(self, host='localhost', port=18888, done_cb=None, **kwargs):
        self.host = host
        self.port = port
        self.cacert_path = kwargs.get('client_cacert', None)

        channel_config = []
        channel_config.append(f'{host}:{port}')

        channel_method = grpc.insecure_channel

        if self.cacert_path:
            with open(self.cacert_path, 'rb') as f:
                cacert = f.read()
            credentials = grpc.ssl_channel_credentials(root_certificates=cacert)
            channel_config.append(credentials)
            channel_method = grpc.secure_channel

        self.channel = channel_method(*channel_config)
        self.stub = raft_pb2_grpc.RaftServiceStub(self.channel)
        self.done_cb = done_cb
        self.address = f'{self.host}:{self.port}'
        self.service = kwargs.get('service', None)

    def AppendEntries(self, request, sync=True, timeout=None, **kwargs):
        logger.info(f'{self.service.state} Send [{self.address}] AppendEntries Request: Term {request.term}')
        future = self.stub.AppendEntries.future(request, timeout=timeout)
        if sync:
            try:
                response = future.result()
                logger.info(f'Get [{self.address}] AppendEntries Response: Term {response.term}')
                return response
            except Exception as exc:
                logger.error(f'{type(exc).__name__} {str(exc)}')
                return None
        if self.done_cb:
            done_cb = partial(self.done_cb, self)
            future.add_done_callback(done_cb)
        return future

    def RequestVote(self, request, sync=True, timeout=None, **kwargs):
        logger.info(f'{self.service.state} Send [{self.address}] RequestVote Request: Term {request.term}')
        future = self.stub.RequestVote.future(request, timeout=timeout)
        if sync:
            response = future.result()
            logger.info(f'Get [{self.address}] RequestVote Response: Term {response.term}')
            return response
        if self.done_cb:
            done_cb = partial(self.done_cb, self)
            future.add_done_callback(done_cb)
        return future
