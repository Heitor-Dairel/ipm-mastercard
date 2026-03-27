from typing import List, Final, Tuple, Dict, Any, Literal, TypeAlias, Optional
from src.helpers import OutgoingFileManager, TupleManagerFile
from src.util import print_custom_text, COLORS, HIGHLIGHTS
from starkbank.iso8583 import mastercard
from starkbank import iso8583
from rich import print
from os import PathLike
import sys
import base64


StrOrBytesPath: TypeAlias = str | bytes | PathLike[str] | PathLike[bytes]
FileDescriptorOrPath: TypeAlias = int | StrOrBytesPath


class ISO8583ParseError(Exception):
    pass


class MastercardISO8583Parse(OutgoingFileManager):

    def __init__(self) -> None:
        super().__init__()

        self._MTI: Final[str] = sys.intern("1240")

    def _read_file(self, path_file: FileDescriptorOrPath) -> bytes:

        with open(file=path_file, mode="rb") as ipm:
            raw = ipm.read()

        return raw

    def _extract_iso_payload(self, raw: bytes, index: int) -> Tuple[bytes, int]:

        START: Final[int] = index
        payload: bytearray = bytearray()
        index_current: int = index
        payload_extend = payload.extend

        while True:
            if index_current + 4 > len(raw):
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
            if index_current + 2 < len(raw) and raw[index_current + 2] == 0:
                break

        return bytes(payload), index_current - START

    def _playload_ipm_file(
        self, raw: bytes
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], int]:

        index: int = 0
        msg_count: int = 0
        parser_mti_main: List[Dict[str, Any]] = []
        parser_mti_secondary: List[Dict[str, Any]] = []

        extract_iso = self._extract_iso_payload
        append_mti_main = parser_mti_main.append
        append_mti_secondary = parser_mti_secondary.append

        while index < len(raw):
            try:
                payload, consumed = extract_iso(raw, index)
                index += consumed

                message_parser: Dict[str, Any] = iso8583.parse(
                    message=payload, template=mastercard, encoding="cp500"
                )

                if sys.intern(message_parser["MTI"]) is self._MTI:
                    de055_base64: bytes = base64.b64decode(message_parser["DE055"])
                    message_parser["DE055"] = de055_base64.hex().upper()
                    append_mti_main(message_parser)
                else:
                    append_mti_secondary(message_parser)

                msg_count += 1

            except Exception as e:
                msg_error = f"Erro na mensagem #{msg_count + 1} (offset {index})"
                raise ISO8583ParseError(msg_error) from e

        return parser_mti_main, parser_mti_secondary, msg_count

    def _logging(
        self, file_name: str, cycle: str, file_dt_time: str, raw: bytes, msg_count: int
    ) -> None:

        LEN_SEPARATOR: Final[int] = 60
        HIGHLIGHT: HIGHLIGHTS = "Bold"
        COLOR_FOREGROUND: COLORS = "OrangeRed1"
        print_custom = print_custom_text

        msg_init: str = (
            f" - FILE: {file_name} \n"
            f" - CYCLE: {cycle}\n"
            f" - DATE/HOUR: {file_dt_time}\n"
            f" - SIZE: {len(raw)} BYTES"
        )
        msg_end: str = f" - TOTAL MESSAGES: {msg_count}"
        msg_separator: str = "=" * LEN_SEPARATOR

        final_logging: str = f"{msg_separator}\n{msg_init}\n{msg_end}\n{msg_separator}"

        print_custom(
            text=final_logging,
            highlight=[HIGHLIGHT],
            color_foreground=COLOR_FOREGROUND,
        )

    def parse_ipm(
        self, date_file: str, cycle: Literal["CIC1", "CIC2", "CIC3"]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:

        path_file, file_name, file_dt_time = self.get_outgoing_files_for_cycle(
            date_file=date_file, cycle=cycle
        )

        raw = self._read_file(path_file=path_file)

        mti_primary, mti_secundary, msg_count = self._playload_ipm_file(raw=raw)

        self._logging(
            file_name=file_name,
            cycle=cycle,
            file_dt_time=file_dt_time,
            raw=raw,
            msg_count=msg_count,
        )

        return mti_primary, mti_secundary


if __name__ == "__main__":

    file = MastercardISO8583Parse()

    iso, iso2 = file.parse_ipm(date_file="26/05/2025", cycle="CIC2")

    print(iso[1])
