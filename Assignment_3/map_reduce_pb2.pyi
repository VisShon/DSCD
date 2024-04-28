from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Point(_message.Message):
    __slots__ = ("x", "y")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    def __init__(self, x: _Optional[float] = ..., y: _Optional[float] = ...) -> None: ...

class MapRequest(_message.Message):
    __slots__ = ("input_split", "centroids")
    INPUT_SPLIT_FIELD_NUMBER: _ClassVar[int]
    CENTROIDS_FIELD_NUMBER: _ClassVar[int]
    input_split: _containers.RepeatedScalarFieldContainer[int]
    centroids: _containers.RepeatedCompositeFieldContainer[Point]
    def __init__(self, input_split: _Optional[_Iterable[int]] = ..., centroids: _Optional[_Iterable[_Union[Point, _Mapping]]] = ...) -> None: ...

class MapOutput(_message.Message):
    __slots__ = ("centroid_id", "point")
    CENTROID_ID_FIELD_NUMBER: _ClassVar[int]
    POINT_FIELD_NUMBER: _ClassVar[int]
    centroid_id: int
    point: Point
    def __init__(self, centroid_id: _Optional[int] = ..., point: _Optional[_Union[Point, _Mapping]] = ...) -> None: ...

class MapResponse(_message.Message):
    __slots__ = ("mapper_id", "status", "map_output")
    MAPPER_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MAP_OUTPUT_FIELD_NUMBER: _ClassVar[int]
    mapper_id: int
    status: str
    map_output: _containers.RepeatedCompositeFieldContainer[MapOutput]
    def __init__(self, mapper_id: _Optional[int] = ..., status: _Optional[str] = ..., map_output: _Optional[_Iterable[_Union[MapOutput, _Mapping]]] = ...) -> None: ...

class IntermediateDataRequest(_message.Message):
    __slots__ = ("reducer_id",)
    REDUCER_ID_FIELD_NUMBER: _ClassVar[int]
    reducer_id: int
    def __init__(self, reducer_id: _Optional[int] = ...) -> None: ...

class IntermediateDataResponse(_message.Message):
    __slots__ = ("map_output", "status")
    MAP_OUTPUT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    map_output: _containers.RepeatedCompositeFieldContainer[MapOutput]
    status: str
    def __init__(self, map_output: _Optional[_Iterable[_Union[MapOutput, _Mapping]]] = ..., status: _Optional[str] = ...) -> None: ...

class ReduceRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class NewCentroids(_message.Message):
    __slots__ = ("centroid_id", "point")
    CENTROID_ID_FIELD_NUMBER: _ClassVar[int]
    POINT_FIELD_NUMBER: _ClassVar[int]
    centroid_id: int
    point: Point
    def __init__(self, centroid_id: _Optional[int] = ..., point: _Optional[_Union[Point, _Mapping]] = ...) -> None: ...

class ReduceResponse(_message.Message):
    __slots__ = ("reducer_id", "status", "new_centroids")
    REDUCER_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    NEW_CENTROIDS_FIELD_NUMBER: _ClassVar[int]
    reducer_id: int
    status: str
    new_centroids: _containers.RepeatedCompositeFieldContainer[NewCentroids]
    def __init__(self, reducer_id: _Optional[int] = ..., status: _Optional[str] = ..., new_centroids: _Optional[_Iterable[_Union[NewCentroids, _Mapping]]] = ...) -> None: ...
