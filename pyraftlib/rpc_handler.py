import logging
from pyraftlib import raft_pb2, raft_pb2_grpc

logger = logging.getLogger(__name__)


class RpcHandler(raft_pb2_grpc.RaftServiceServicer):
    def __init__(self, cluster, service):
        self.cluster = cluster
        self.service = service

    def AppendEntries(self, request, context):
        logger.info(f'{self.service.state} AppendEntries Term {request.term} from Peer {request.leaderId}')
        response = self.cluster.on_peer_append_entries(request)
        return response

    def RequestVote(self, request, context):
        logger.info(f'{self.service.state} RequestVote Term {request.term} from Peer {request.candidateId}')
        response = self.cluster.on_peer_vote_request(request)
        return response
