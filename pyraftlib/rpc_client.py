import logging
import grpc

from pyraftlib import raft_pb2_grpc, raft_pb2

logger = logging.getLogger(__name__)


class RpcClient:
    def __init__(self, host='localhost', port=18888, **kwargs):
        self.host = host
        self.port = port
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = raft_pb2_grpc.RaftServiceStub(self.channel)

    def AppendEntries(self, request, sync=True):
        logger.info(f'Send AppendEntries Request: Term {request.term}')
        future = self.stub.AppendEntries.future(request)
        if sync:
            response = future.result()
            logger.info(f'Get AppendEntries Response: Term {response.term}')
            return response
        return future

    def RequestVote(self, request, sync=True):
        logger.info(f'Send RequestVote Request: Term {request.term}')
        future = self.stub.RequestVote.future(request)
        if sync:
            response = future.result()
            logger.info(f'Get RequestVote Response: Term {response.term}')
            return response
        return future
