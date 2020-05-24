import logging
from pyraftlib import raft_pb2, raft_pb2_grpc

logger = logging.getLogger(__name__)


class RpcHandler(raft_pb2_grpc.RaftServiceServicer):
    def __init__(self, cluster, service):
        self.cluster = cluster
        self.service = service

    def AppendEntries(self, request, context):
        logger.info(f'{self.service.state} AppendEntries Term {request.term} PeerInfo {self.cluster.peer_info}')
        # response = raft_pb2.AppendEntriesResponse(term=1, success=True, peer_id=self.cluster.peer_info['peer_id'])
        response = self.cluster.on_peer_append_entries(request)
        return response

    def RequestVote(self, request, context):
        logger.info(f'{self.service.state} RequestVote Term {request.term} from Peer {request.candidateId}')
        response = self.cluster.on_peer_vote_request(request)
        # response = raft_pb2.RequestVoteResponse(term=1, voteGranted=True, peer_id=self.cluster.peer_info['peer_id'])
        return response
