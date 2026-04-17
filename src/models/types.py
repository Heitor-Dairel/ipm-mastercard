from typing import List, Dict, Any, Union, Literal, NamedTuple

type ParseDb = List[List[Union[int, str, float, None]]]
type ParseIPM = List[Dict[str, Any]]
type CycleIPM = Literal["CIC1", "CIC2", "CIC3"]


class TupleManagerFile(NamedTuple):

    file_name: str
    bytes_file: memoryview
