from typing import (
    Final,
    Dict,
    Literal,
    NamedTuple,
    Iterator,
    TypeAlias,
    Optional,
)
from pathlib import Path
from datetime import datetime
from rich import print

_BASE_DIR: Final[Path] = Path(
    r"C:\Users\heitor.tavares\OneDrive - TRIVALE ADMINISTRACAO LTDA"
    r"\Operação Processadora - Arquivos CSU"
)
_FLAG_FOLDER: Final[str] = "(1)"


class TupleManagerFile(NamedTuple):

    file_name: str
    bytes_file: memoryview


FileLoadData: TypeAlias = Dict[str, Dict[str, TupleManagerFile]]
FileLoadProcessadora: TypeAlias = Dict[str, Dict[str, TupleManagerFile]]


class DateInvalidFormat(ValueError): ...


def _validate_date(date: str) -> None:

    formato: str = "%d/%m/%Y"
    msg: str = f"Formato de data está inválido '{date}'"
    try:
        datetime.strptime(date, formato)
    except ValueError as e:
        raise DateInvalidFormat(msg) from e


def _get_bytes(file_path: Path) -> memoryview:
    data_bytes: bytes = file_path.read_bytes()
    raw: memoryview = memoryview(data_bytes)

    return raw


def search_arq(
    file_date: str, cycle: Literal["CIC1", "CIC2", "CIC3"]
) -> Optional[TupleManagerFile]:

    _validate_date(date=file_date)

    file_date_format: str = datetime.strptime(file_date, "%d/%m/%Y").strftime("%d%m%Y")
    files: Final[Iterator[Path]] = _BASE_DIR.rglob(
        f"CSU_ACQ_MASTER_OUTGOING_{cycle}_{file_date_format}*.TXT"
    )

    file: Optional[TupleManagerFile] = None

    for arq in files:

        if _FLAG_FOLDER not in arq.parent.name:

            raw: memoryview = _get_bytes(arq)
            file = TupleManagerFile(
                file_name=arq.stem,
                bytes_file=raw,
            )

    return file


if __name__ == "__main__":

    arq = search_arq(file_date="20/03/2026", cycle="CIC1")

    print(arq)
