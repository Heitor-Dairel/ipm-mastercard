from typing import List, Final, Tuple, Dict, Any, Literal
from src.helpers import OutgoingFileManager
from starkbank.iso8583 import mastercard
from starkbank import iso8583
from pathlib import Path
import sys
import base64


class ISO8583ParseError(Exception):
    pass


class MastercardISO8583Parse(OutgoingFileManager):

    def __init__(self) -> None:
        super().__init__()

        self._MTI: Final[str] = "1240"

    def _extract_iso_payload(
        self, raw: memoryview, index: int, len_raw: int
    ) -> Tuple[bytes, int]:

        START: Final[int] = index
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

        return bytes(payload), index_current - START

    def _playload_ipm_file(
        self,
        raw: memoryview,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:

        LEN_RAW: Final[int] = len(raw)
        index: int = 0
        msg_count: int = 0
        parser_mti_main: List[Dict[str, Any]] = []
        parser_mti_secondary: List[Dict[str, Any]] = []
        extract_iso = self._extract_iso_payload
        append_mti_main = parser_mti_main.append
        append_mti_secondary = parser_mti_secondary.append

        while index < LEN_RAW:
            try:
                payload, consumed = extract_iso(raw=raw, index=index, len_raw=LEN_RAW)
                index += consumed

                message_parser: Dict[str, Any] = iso8583.parse(
                    message=payload, template=mastercard, encoding="cp500"
                )

                if message_parser["MTI"] == self._MTI:
                    de055_current: bytes = message_parser["DE055"]
                    de055_base64: bytes = base64.b64decode(de055_current)
                    message_parser["DE055"] = de055_base64.hex().upper()
                    append_mti_main(message_parser)
                else:
                    append_mti_secondary(message_parser)

                msg_count += 1

            except Exception as e:
                msg_error = f"Erro na mensagem #{msg_count + 1} (offset {index})"
                raise ISO8583ParseError(msg_error) from e

        return parser_mti_main, parser_mti_secondary

    def file_contents(
        self, date_file: str, cycle: Literal["CIC1", "CIC2", "CIC3"]
    ) -> memoryview:

        path_file, _, _ = self.get_outgoing_files_for_cycle(
            date_file=date_file, cycle=cycle
        )

        data: bytes = Path(path_file).read_bytes()

        raw: memoryview = memoryview(data)

        return raw

    def parse_ipm(
        self, raw: memoryview
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:

        mti_primary, mti_secundary = self._playload_ipm_file(
            raw=raw,
        )

        return mti_primary, mti_secundary


if __name__ == "__main__":

    file = MastercardISO8583Parse()

    raw = file.file_contents(date_file="26/05/2025", cycle="CIC2")

    iso, iso2 = file.parse_ipm(raw=raw)

    # print(iso[1])
