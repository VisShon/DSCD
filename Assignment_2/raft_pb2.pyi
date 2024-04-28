from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class VoteRequest(_message.Message):
    __slots__ = ("term", "candidateId", "lastLogIndex", "lastLogTerm")
    TERM_FIELD_NUMBER: _ClassVar[int]
    CANDIDATEID_FIELD_NUMBER: _ClassVar[int]
    LASTLOGINDEX_FIELD_NUMBER: _ClassVar[int]
    LASTLOGTERM_FIELD_NUMBER: _ClassVar[int]
    term: int
    candidateId: int
    lastLogIndex: int
    lastLogTerm: int
    def __init__(self, term: _Optional[int] = ..., candidateId: _Optional[int] = ..., lastLogIndex: _Optional[int] = ..., lastLogTerm: _Optional[int] = ...) -> None: ...

class VoteResponse(_message.Message):
    __slots__ = ("nodeId", "term", "voteGranted", "leaderLease")
    NODEID_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    VOTEGRANTED_FIELD_NUMBER: _ClassVar[int]
    LEADERLEASE_FIELD_NUMBER: _ClassVar[int]
    nodeId: int
    term: int
    voteGranted: bool
    leaderLease: float
    def __init__(self, nodeId: _Optional[int] = ..., term: _Optional[int] = ..., voteGranted: bool = ..., leaderLease: _Optional[float] = ...) -> None: ...

class SuffixEntry(_message.Message):
    __slots__ = ("op", "key", "value", "term")
    OP_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    op: str
    key: str
    value: str
    term: int
    def __init__(self, op: _Optional[str] = ..., key: _Optional[str] = ..., value: _Optional[str] = ..., term: _Optional[int] = ...) -> None: ...

class LogRequest(_message.Message):
    __slots__ = ("leaderId", "currentTerm", "prefixLen", "prefixTerm", "commitLength", "suffix", "leaderLease")
    LEADERID_FIELD_NUMBER: _ClassVar[int]
    CURRENTTERM_FIELD_NUMBER: _ClassVar[int]
    PREFIXLEN_FIELD_NUMBER: _ClassVar[int]
    PREFIXTERM_FIELD_NUMBER: _ClassVar[int]
    COMMITLENGTH_FIELD_NUMBER: _ClassVar[int]
    SUFFIX_FIELD_NUMBER: _ClassVar[int]
    LEADERLEASE_FIELD_NUMBER: _ClassVar[int]
    leaderId: int
    currentTerm: int
    prefixLen: int
    prefixTerm: int
    commitLength: int
    suffix: _containers.RepeatedCompositeFieldContainer[SuffixEntry]
    leaderLease: float
    def __init__(self, leaderId: _Optional[int] = ..., currentTerm: _Optional[int] = ..., prefixLen: _Optional[int] = ..., prefixTerm: _Optional[int] = ..., commitLength: _Optional[int] = ..., suffix: _Optional[_Iterable[_Union[SuffixEntry, _Mapping]]] = ..., leaderLease: _Optional[float] = ...) -> None: ...

class LogResponse(_message.Message):
    __slots__ = ("nodeId", "term", "ack", "success")
    NODEID_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    ACK_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    nodeId: int
    term: int
    ack: int
    success: bool
    def __init__(self, nodeId: _Optional[int] = ..., term: _Optional[int] = ..., ack: _Optional[int] = ..., success: bool = ...) -> None: ...

class ServeClientArgs(_message.Message):
    __slots__ = ("Request",)
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    Request: str
    def __init__(self, Request: _Optional[str] = ...) -> None: ...

class ServeClientReply(_message.Message):
    __slots__ = ("Data", "LeaderID", "Success")
    DATA_FIELD_NUMBER: _ClassVar[int]
    LEADERID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    Data: str
    LeaderID: str
    Success: bool
    def __init__(self, Data: _Optional[str] = ..., LeaderID: _Optional[str] = ..., Success: bool = ...) -> None: ...
