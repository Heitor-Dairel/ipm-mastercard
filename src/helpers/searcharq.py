from typing import Final, Dict, List, Literal, NamedTuple, Iterator, TypeAlias
from pathlib import Path
from datetime import datetime
from rich import print


FORMAT_DATE_TIME: Final[str] = "%d/%m/%Y %H:%M:%S"
FORMAT_DATE: Final[str] = "%d/%m/%Y"


def get_bytes_to_file(file_path: Path) -> memoryview:
    data_bytes: bytes = file_path.read_bytes()
    raw: memoryview = memoryview(data_bytes)

    return raw


class TupleManagerFile(NamedTuple):

    file_name: str
    file_dt_time: str
    bytes_file: memoryview


FileLoadData: TypeAlias = Dict[str, Dict[str, TupleManagerFile]]
FileLoadProcessadora: TypeAlias = Dict[str, Dict[str, TupleManagerFile]]


class DateInvalidError(ValueError): ...


class MissingFileForDateError(ValueError): ...


class MissingCycleForDateError(ValueError): ...


class FileManagerProcessadora:

    def __init__(self) -> None:

        self._OUTGOING_FILES: Final[FileLoadProcessadora] = self._load_outgoing_files()

    def _load_outgoing_files(self) -> FileLoadProcessadora:

        BASE_DIR: Final[Path] = Path(
            r"C:\Users\heitor.tavares\OneDrive - TRIVALE ADMINISTRACAO LTDA"
            r"\Operação Processadora - Arquivos CSU"
        )
        FLAG_FOLDER: Final[str] = "(1)"
        arquivos: Final[Iterator[Path]] = BASE_DIR.rglob(
            "CSU_ACQ_MASTER_OUTGOING_*.TXT"
        )

        dict_outgoing_arq: Dict[str, Dict[str, TupleManagerFile]] = {}

        for arq in arquivos:

            if FLAG_FOLDER not in arq.parent.name:

                parts_nam_file: List[str] = arq.stem.split("_")

                clico_outgoing_master: str = parts_nam_file[-3]
                dt_file: str = parts_nam_file[-2]
                time_file: str = parts_nam_file[-1]

                f_dt_time_str: str = datetime.strptime(
                    f"{dt_file} {time_file}", "%d%m%Y %H%M%S"
                ).strftime(FORMAT_DATE_TIME)
                f_dt_str: str = datetime.strptime(dt_file, "%d%m%Y").strftime(
                    FORMAT_DATE
                )

                if f_dt_str not in dict_outgoing_arq:
                    dict_outgoing_arq[f_dt_str] = {}

                raw: memoryview = get_bytes_to_file(arq.resolve())
                dict_outgoing_arq[f_dt_str][clico_outgoing_master] = TupleManagerFile(
                    file_name=arq.name,
                    file_dt_time=f_dt_time_str,
                    bytes_file=raw,
                )

        return dict_outgoing_arq

    def get_files_for_cycle(
        self, date_file: str, cycle: Literal["CIC1", "CIC2", "CIC3"]
    ) -> TupleManagerFile:

        msg: str = ""

        if date_file not in self._OUTGOING_FILES:

            msg = f"Não existe arquivo para a data '{date_file}'"
            raise MissingFileForDateError(msg)

        if cycle not in self._OUTGOING_FILES[date_file]:

            msg = f"O ciclo '{cycle}' não foi encontrado para a data '{date_file}'"

            raise MissingCycleForDateError(msg)

        return self._OUTGOING_FILES[date_file][cycle]

    def get_files_for_date(self, date_file: str) -> Dict[str, TupleManagerFile]:

        msg: str = ""

        if date_file not in self._OUTGOING_FILES:

            msg = f"Não existe arquivo para a data '{date_file}'"
            raise MissingFileForDateError(msg)

        return self._OUTGOING_FILES[date_file]

    def get_all_files(self) -> FileLoadProcessadora:

        return self._OUTGOING_FILES


class FileManagerData:

    def __init__(self) -> None:

        self._OUTGOING_FILES: Final[FileLoadData] = self._load_outgoing_files()

    def _load_outgoing_files(self) -> FileLoadData:

        BASE_DIR: Final[Path] = Path(__file__).parent.parent.parent
        DATA_DIR = BASE_DIR / "data"
        arquivos = DATA_DIR.glob("CSU_ACQ_MASTER_OUTGOING_*.TXT")
        dict_outgoing_arq: FileLoadData = {}
        for arq in arquivos:
            parts_nam_file: List[str] = arq.stem.split("_")
            clico_outgoing_master: str = parts_nam_file[-3]
            dt_file: str = parts_nam_file[-2]
            time_file: str = parts_nam_file[-1]

            f_dt_time_str: str = datetime.strptime(
                f"{dt_file} {time_file}", "%d%m%Y %H%M%S"
            ).strftime(FORMAT_DATE_TIME)
            f_dt_str: str = datetime.strptime(dt_file, "%d%m%Y").strftime(FORMAT_DATE)

            if f_dt_str not in dict_outgoing_arq:
                dict_outgoing_arq[f_dt_str] = {}

            raw: memoryview = get_bytes_to_file(arq.resolve())
            dict_outgoing_arq[f_dt_str][clico_outgoing_master] = TupleManagerFile(
                file_name=arq.name,
                file_dt_time=f_dt_time_str,
                bytes_file=raw,
            )
        return dict_outgoing_arq

    def get_files_for_cycle(
        self, date_file: str, cycle: Literal["CIC1", "CIC2", "CIC3"]
    ) -> TupleManagerFile:

        msg: str = ""

        if date_file not in self._OUTGOING_FILES:

            msg = f"Não existe arquivo para a data '{date_file}'"
            raise MissingFileForDateError(msg)

        if cycle not in self._OUTGOING_FILES[date_file]:

            msg = f"O ciclo '{cycle}' não foi encontrado para a data '{date_file}'"

            raise MissingCycleForDateError(msg)

        return self._OUTGOING_FILES[date_file][cycle]

    def get_files_for_date(self, date_file: str) -> Dict[str, TupleManagerFile]:

        msg: str = ""

        if date_file not in self._OUTGOING_FILES:

            msg = f"Não existe arquivo para a data '{date_file}'"
            raise MissingFileForDateError(msg)

        return self._OUTGOING_FILES[date_file]

    def get_all_files(self) -> FileLoadData:

        return self._OUTGOING_FILES


if __name__ == "__main__":

    arq = FileManagerProcessadora()

    a = arq.get_files_for_cycle(date_file="25/06/2025", cycle="CIC2")

    print(a.bytes_file)

    print(FileManagerData().get_files_for_date(date_file="26/05/2025"))
