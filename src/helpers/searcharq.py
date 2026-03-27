from typing import Final, Dict, List, Literal, Union, NamedTuple
from pathlib import Path
from datetime import datetime
from rich import print
import sys


class TupleManagerFile(NamedTuple):

    path: Path
    file_name: str
    file_dt_time: str


class DateInvalidError(ValueError):
    pass


class MissingFileForDateError(ValueError):
    pass


class MissingCycleForDateError(ValueError):
    pass


class OutgoingFileManager:

    def __init__(self) -> None:

        self.OUTGOING_FILES: Final[Dict[str, Dict[str, TupleManagerFile]]] = (
            self._load_outgoing_files()
        )

    def _load_outgoing_files(self) -> Dict[str, Dict[str, TupleManagerFile]]:

        PATH_FILE_OUTGOING_MASTERCARD: Final[Path] = Path(
            r"C:\Users\heitor.tavares\OneDrive - TRIVALE ADMINISTRACAO LTDA"
            r"\Operação Processadora - Arquivos CSU"
        )
        FORMAT_DATE_TIME: Final[str] = "%d/%m/%Y %H:%M:%S"
        FORMAT_DATE: Final[str] = "%d/%m/%Y"
        LIKE_PATH_OUTGOING: Final[str] = "CSU_ACQ_MASTER_OUTGOING_*.TXT"
        FLAG_FOLDER: Final[str] = "(1)"

        dict_outgoing_arq: Dict[str, Dict[str, TupleManagerFile]] = {}

        for arq in PATH_FILE_OUTGOING_MASTERCARD.rglob(LIKE_PATH_OUTGOING):

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

                dict_outgoing_arq[f_dt_str][clico_outgoing_master] = TupleManagerFile(
                    path=arq.resolve(),
                    file_name=arq.name,
                    file_dt_time=f_dt_time_str,
                )

        return dict_outgoing_arq

    def get_outgoing_files_for_cycle(
        self, date_file: str, cycle: Literal["CIC1", "CIC2", "CIC3"]
    ) -> TupleManagerFile:

        msg: str = ""

        if date_file not in self.OUTGOING_FILES:

            msg = f"Não existe arquivo para a data '{date_file}'"
            raise MissingFileForDateError(msg)

        if cycle is not None and cycle not in self.OUTGOING_FILES[date_file]:

            msg = f"O ciclo '{cycle}' não foi encontrado para a data '{date_file}'"

            raise MissingCycleForDateError(msg)

        return self.OUTGOING_FILES[date_file][cycle]

    def get_outgoing_files_for_date(
        self, date_file: str
    ) -> Dict[str, TupleManagerFile]:

        msg: str = ""

        if date_file not in self.OUTGOING_FILES:

            msg = f"Não existe arquivo para a data '{date_file}'"
            raise MissingFileForDateError(msg)

        return self.OUTGOING_FILES[date_file]

    def get_all_outgoing_files(self) -> Dict[str, Dict[str, TupleManagerFile]]:

        return self.OUTGOING_FILES


if __name__ == "__main__":

    arq = OutgoingFileManager()

    a = arq.get_outgoing_files_for_date(date_file="25/06/2025")

    print(a)
