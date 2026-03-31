from typing import Union
from .searcharq import FileManagerProcessadora, FileManagerData, TupleManagerFile
from .filedata import FilesDataSaving


def get_model_path_file(
    path_search_model: bool = True,
) -> Union[FileManagerProcessadora, FileManagerData]:

    if path_search_model:

        return FileManagerProcessadora()

    return FileManagerData()


__all__ = ["get_model_path_file", "TupleManagerFile", "FilesDataSaving"]
