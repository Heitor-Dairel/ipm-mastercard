from typing import List, Final, Tuple, Dict, Any, Literal, Optional, Set
from ..helpers import get_model_path_file, FilesDataSaving
from ..template import mastercard
from ..util import print_custom_text
from starkbank import iso8583


class ISO8583ParseError(Exception): ...


class MastercardISO8583Parse(FilesDataSaving):

    def __init__(self, path_search_model: bool = True) -> None:
        super().__init__()
        self._MTI: Final[str] = "1240"
        self._file_name: str = ""
        self._file_dt_time: str = ""
        self._file_cycle: str = ""
        self._path_search_model = get_model_path_file(
            path_search_model=path_search_model
        )

    def _extract_iso_payload(
        self, raw: memoryview, index: int, len_raw: int
    ) -> Tuple[bytes, int]:

        start: int = index
        payload: bytearray = bytearray()
        index_current: int = index
        payload_extend = payload.extend

        while True:
            if index_current + 4 > len_raw:
                break

            seg_id: int = raw[index_current + 2] & 0xFF
            seg_len: int = ((raw[index_current] & 0xFF) << 8) | (
                raw[index_current + 1] & 0xFF
            )

            payload_len: int = seg_len - 4
            payload_extend(raw[index_current + 4 : index_current + 4 + payload_len])
            index_current += 4 + payload_len

            if seg_id == 0:
                break
            if index_current + 2 < len_raw and raw[index_current + 2] == 0:
                break

        return bytes(payload), index_current - start

    def _playload_ipm_file(
        self, raw: memoryview, logging: bool = True
    ) -> List[Dict[str, Any]]:

        len_raw: int = len(raw)
        index: int = 0
        msg_count: int = 0
        parse_mti: List[Dict[str, Any]] = []
        extract_iso = self._extract_iso_payload
        append_mti = parse_mti.append

        try:
            while index < len_raw:

                payload, consumed = extract_iso(raw=raw, index=index, len_raw=len_raw)
                index += consumed

                message_parser: Dict[str, Any] = iso8583.parse(
                    message=payload, template=mastercard, encoding="cp500"
                )

                append_mti(message_parser)

                msg_count += 1

        except Exception as e:
            msg_error = f"Erro na mensagem #{msg_count + 1} (offset {index})"
            raise ISO8583ParseError(msg_error) from e

        if logging:
            self._logging(
                file_name=self._file_name,
                cycle=self._file_cycle,
                file_dt_time=self._file_dt_time,
                row_count=msg_count,
            )

        self._output_txt(parse=parse_mti)

        return parse_mti

    def _logging(
        self,
        file_name: Optional[str],
        cycle: Optional[str],
        file_dt_time: Optional[str],
        row_count: int,
    ) -> None:

        separator: str = "=" * 63

        body: str = (
            f"{separator}\n - FILE NAME: {file_name}\n"
            f" - DATE/HOUR: {file_dt_time}\n"
            f" - CYCLE: {cycle}\n"
            f" - ROW COUNT: {row_count}\n"
            f"{separator}\n\n"
        )

        print_custom_text(text=body, highlight=["Bold"], color_foreground="OrangeRed1")

    def _output_txt(self, parse: List[Dict[str, Any]]):

        self.save_txt(data=parse, file_name=self._file_name[:-4])

    def _clean_parse(
        self, parse: List[Dict[str, Any]], field: List[str], enable_field: bool = False
    ) -> Tuple[List[str], List[Dict[str, Any]]]:

        data_elements: List[Dict[str, Any]] = []
        append_data_elements = data_elements.append
        elements: Set[str] = set(field)
        trash_elements: Final[Set[str]] = {"BMP", "DE001", "PDS", "Length"}
        elements.update(trash_elements)

        for i in parse:

            if i["MTI"] == "1240":

                data: Dict[str, Any] = {}

                if not enable_field:

                    for key, item in i.items():
                        if key not in elements:
                            data[key] = item

                    for key, item in i["PDS"].items():
                        if key not in elements:
                            data[key] = item

                if enable_field:

                    for key, item in i.items():
                        if key in elements and key not in trash_elements:
                            data[key] = item

                    for key, item in i["PDS"].items():
                        if key in elements and key not in trash_elements:
                            data[key] = item

                append_data_elements(data)

        headerd_elements: List[str] = [key for key, _ in data_elements[0].items()]

        return headerd_elements, data_elements

    def parse_ipm(
        self,
        date_file: str,
        cycle: Literal["CIC1", "CIC2", "CIC3"],
        logging: bool = True,
    ) -> List[Dict[str, Any]]:

        self._file_cycle = cycle

        self._file_name, self._file_dt_time, bytes_file = (
            self._path_search_model.get_files_for_cycle(
                date_file=date_file, cycle=cycle
            )
        )

        return self._playload_ipm_file(raw=bytes_file, logging=logging)

    def output_excel(
        self,
        parse: List[Dict[str, Any]],
        field: List[str],
        enable_field: bool = False,
    ) -> None:
        header, data = self._clean_parse(
            parse=parse, field=field, enable_field=enable_field
        )
        self.save_csv(data=data, headers=header, file_name=self._file_name[:-4])


if __name__ == "__main__":

    file = MastercardISO8583Parse()
    iso = file.parse_ipm(date_file="26/05/2025", cycle="CIC2")

    # print(iso[1])
