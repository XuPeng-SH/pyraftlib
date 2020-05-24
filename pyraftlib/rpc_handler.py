import logging
from pyraftlib import raft_pb2, raft_pb2_grpc

logger = logging.getLogger(__name__)


class RpcHandler(raft_pb2_grpc.RaftServiceServicer):
    def __init__(self, cluster):
        self.cluster = cluster

    def AppendEntries(self, request, context):
        logger.info(f'AppendEntries Term {request.term}')
        response = raft_pb2.AppendEntriesResponse(term=1, success=True, peer_id=self.cluster.peer_id)
        return response

    def RequestVote(self, request, context):
        logger.info(f'RequestVote Term {request.term}')
        response = raft_pb2.RequestVoteResponse(term=1, voteGranted=True, peer_id=self.cluster.peer_id)
        return response
