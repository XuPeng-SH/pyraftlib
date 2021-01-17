# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: raft.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='raft.proto',
  package='raft',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=b'\n\nraft.proto\x12\x04raft\"D\n\x08LogEntry\x12\x0c\n\x04noop\x18\x01 \x01(\x08\x12\x0c\n\x04term\x18\x02 \x01(\x04\x12\r\n\x05index\x18\x03 \x01(\x04\x12\r\n\x05\x65ntry\x18\x04 \x01(\x0c\"\x99\x01\n\x14\x41ppendEntriesRequest\x12\x0c\n\x04term\x18\x01 \x01(\x04\x12\x10\n\x08leaderId\x18\x02 \x01(\x04\x12\x14\n\x0cprevLogIndex\x18\x03 \x01(\x04\x12\x13\n\x0bprevLogTerm\x18\x04 \x01(\x04\x12\x0f\n\x07\x65ntries\x18\x05 \x03(\x0c\x12\x14\n\x0cleaderCommit\x18\x06 \x01(\x04\x12\x0f\n\x07peer_id\x18\x07 \x01(\x04\"]\n\x15\x41ppendEntriesResponse\x12\x0c\n\x04term\x18\x01 \x01(\x04\x12\x0f\n\x07success\x18\x02 \x01(\x08\x12\x0f\n\x07peer_id\x18\x03 \x01(\x04\x12\x14\n\x0crequest_term\x18\x04 \x01(\x04\"s\n\x12RequestVoteRequest\x12\x0c\n\x04term\x18\x01 \x01(\x04\x12\x13\n\x0b\x63\x61ndidateId\x18\x02 \x01(\x04\x12\x14\n\x0clastLogIndex\x18\x03 \x01(\x04\x12\x13\n\x0blastLogTerm\x18\x04 \x01(\x04\x12\x0f\n\x07peer_id\x18\x05 \x01(\x04\"I\n\x13RequestVoteResponse\x12\x0c\n\x04term\x18\x01 \x01(\x04\x12\x13\n\x0bvoteGranted\x18\x02 \x01(\x08\x12\x0f\n\x07peer_id\x18\x03 \x01(\x04\x32\x9f\x01\n\x0bRaftService\x12J\n\rAppendEntries\x12\x1a.raft.AppendEntriesRequest\x1a\x1b.raft.AppendEntriesResponse\"\x00\x12\x44\n\x0bRequestVote\x12\x18.raft.RequestVoteRequest\x1a\x19.raft.RequestVoteResponse\"\x00\x62\x06proto3'
)




_LOGENTRY = _descriptor.Descriptor(
  name='LogEntry',
  full_name='raft.LogEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='noop', full_name='raft.LogEntry.noop', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='term', full_name='raft.LogEntry.term', index=1,
      number=2, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='index', full_name='raft.LogEntry.index', index=2,
      number=3, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='entry', full_name='raft.LogEntry.entry', index=3,
      number=4, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=20,
  serialized_end=88,
)


_APPENDENTRIESREQUEST = _descriptor.Descriptor(
  name='AppendEntriesRequest',
  full_name='raft.AppendEntriesRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='term', full_name='raft.AppendEntriesRequest.term', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='leaderId', full_name='raft.AppendEntriesRequest.leaderId', index=1,
      number=2, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='prevLogIndex', full_name='raft.AppendEntriesRequest.prevLogIndex', index=2,
      number=3, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='prevLogTerm', full_name='raft.AppendEntriesRequest.prevLogTerm', index=3,
      number=4, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='entries', full_name='raft.AppendEntriesRequest.entries', index=4,
      number=5, type=12, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='leaderCommit', full_name='raft.AppendEntriesRequest.leaderCommit', index=5,
      number=6, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='peer_id', full_name='raft.AppendEntriesRequest.peer_id', index=6,
      number=7, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=91,
  serialized_end=244,
)


_APPENDENTRIESRESPONSE = _descriptor.Descriptor(
  name='AppendEntriesResponse',
  full_name='raft.AppendEntriesResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='term', full_name='raft.AppendEntriesResponse.term', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='success', full_name='raft.AppendEntriesResponse.success', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='peer_id', full_name='raft.AppendEntriesResponse.peer_id', index=2,
      number=3, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='request_term', full_name='raft.AppendEntriesResponse.request_term', index=3,
      number=4, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=246,
  serialized_end=339,
)


_REQUESTVOTEREQUEST = _descriptor.Descriptor(
  name='RequestVoteRequest',
  full_name='raft.RequestVoteRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='term', full_name='raft.RequestVoteRequest.term', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='candidateId', full_name='raft.RequestVoteRequest.candidateId', index=1,
      number=2, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='lastLogIndex', full_name='raft.RequestVoteRequest.lastLogIndex', index=2,
      number=3, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='lastLogTerm', full_name='raft.RequestVoteRequest.lastLogTerm', index=3,
      number=4, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='peer_id', full_name='raft.RequestVoteRequest.peer_id', index=4,
      number=5, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=341,
  serialized_end=456,
)


_REQUESTVOTERESPONSE = _descriptor.Descriptor(
  name='RequestVoteResponse',
  full_name='raft.RequestVoteResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='term', full_name='raft.RequestVoteResponse.term', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='voteGranted', full_name='raft.RequestVoteResponse.voteGranted', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='peer_id', full_name='raft.RequestVoteResponse.peer_id', index=2,
      number=3, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=458,
  serialized_end=531,
)

DESCRIPTOR.message_types_by_name['LogEntry'] = _LOGENTRY
DESCRIPTOR.message_types_by_name['AppendEntriesRequest'] = _APPENDENTRIESREQUEST
DESCRIPTOR.message_types_by_name['AppendEntriesResponse'] = _APPENDENTRIESRESPONSE
DESCRIPTOR.message_types_by_name['RequestVoteRequest'] = _REQUESTVOTEREQUEST
DESCRIPTOR.message_types_by_name['RequestVoteResponse'] = _REQUESTVOTERESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

LogEntry = _reflection.GeneratedProtocolMessageType('LogEntry', (_message.Message,), {
  'DESCRIPTOR' : _LOGENTRY,
  '__module__' : 'raft_pb2'
  # @@protoc_insertion_point(class_scope:raft.LogEntry)
  })
_sym_db.RegisterMessage(LogEntry)

AppendEntriesRequest = _reflection.GeneratedProtocolMessageType('AppendEntriesRequest', (_message.Message,), {
  'DESCRIPTOR' : _APPENDENTRIESREQUEST,
  '__module__' : 'raft_pb2'
  # @@protoc_insertion_point(class_scope:raft.AppendEntriesRequest)
  })
_sym_db.RegisterMessage(AppendEntriesRequest)

AppendEntriesResponse = _reflection.GeneratedProtocolMessageType('AppendEntriesResponse', (_message.Message,), {
  'DESCRIPTOR' : _APPENDENTRIESRESPONSE,
  '__module__' : 'raft_pb2'
  # @@protoc_insertion_point(class_scope:raft.AppendEntriesResponse)
  })
_sym_db.RegisterMessage(AppendEntriesResponse)

RequestVoteRequest = _reflection.GeneratedProtocolMessageType('RequestVoteRequest', (_message.Message,), {
  'DESCRIPTOR' : _REQUESTVOTEREQUEST,
  '__module__' : 'raft_pb2'
  # @@protoc_insertion_point(class_scope:raft.RequestVoteRequest)
  })
_sym_db.RegisterMessage(RequestVoteRequest)

RequestVoteResponse = _reflection.GeneratedProtocolMessageType('RequestVoteResponse', (_message.Message,), {
  'DESCRIPTOR' : _REQUESTVOTERESPONSE,
  '__module__' : 'raft_pb2'
  # @@protoc_insertion_point(class_scope:raft.RequestVoteResponse)
  })
_sym_db.RegisterMessage(RequestVoteResponse)



_RAFTSERVICE = _descriptor.ServiceDescriptor(
  name='RaftService',
  full_name='raft.RaftService',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=534,
  serialized_end=693,
  methods=[
  _descriptor.MethodDescriptor(
    name='AppendEntries',
    full_name='raft.RaftService.AppendEntries',
    index=0,
    containing_service=None,
    input_type=_APPENDENTRIESREQUEST,
    output_type=_APPENDENTRIESRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='RequestVote',
    full_name='raft.RaftService.RequestVote',
    index=1,
    containing_service=None,
    input_type=_REQUESTVOTEREQUEST,
    output_type=_REQUESTVOTERESPONSE,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_RAFTSERVICE)

DESCRIPTOR.services_by_name['RaftService'] = _RAFTSERVICE

# @@protoc_insertion_point(module_scope)
