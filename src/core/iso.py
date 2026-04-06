from typing import List, Final, Tuple, Dict, Any, Literal, Optional
from ..helpers import search_arq, FilesDataSaving, TupleManagerFile
from ..template import mastercard
from ..util import print_custom_text
from starkbank import iso8583


class ISO8583ParseError(Exception): ...


class MastercardISO8583Parse(FilesDataSaving):

    def __init__(self) -> None:
        super().__init__()
        self._MTI: Final[str] = "1240"
        self._file_name: Optional[str] = ""
        self._file_cycle: str = ""

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
                row_count=msg_count,
            )

        self._output_txt_logging(parse=parse_mti)

        return parse_mti

    def _logging(
        self,
        file_name: Optional[str],
        cycle: Optional[str],
        row_count: int,
    ) -> None:

        separator: str = "=" * 63

        body: str = (
            f"{separator}\n"
            f" - FILE NAME: {file_name}\n"
            f" - CYCLE: {cycle}\n"
            f" - ROW COUNT: {row_count}\n"
            f"{separator}\n\n"
        )

        print_custom_text(text=body, highlight=["Bold"], color_foreground="OrangeRed1")

    def _output_txt_logging(self, parse: List[Dict[str, Any]]) -> None:

        if self._file_name:

            self.save_txt(data=parse, file_name=self._file_name)

    def parse_ipm(
        self,
        date_file: str,
        cycle: Literal["CIC1", "CIC2", "CIC3"],
        logging: bool = True,
    ) -> Optional[List[Dict[str, Any]]]:

        self._file_cycle = cycle

        file_infos: Optional[TupleManagerFile] = search_arq(
            file_date=date_file, cycle=cycle
        )

        if file_infos:

            self._file_name, bytes_file = file_infos

            return self._playload_ipm_file(raw=bytes_file, logging=logging)

        return None


if __name__ == "__main__":

    file = MastercardISO8583Parse()
    iso = file.parse_ipm(date_file="26/05/2025", cycle="CIC2")

    # print(iso[1])
