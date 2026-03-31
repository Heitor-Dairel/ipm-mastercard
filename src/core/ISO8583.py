from typing import List, Final, Tuple, Dict, Any, Literal
from ..helpers import get_model_path_file
from ..template import mastercard
from starkbank import iso8583


class ISO8583ParseError(Exception): ...


class MastercardISO8583Parse:

    def __init__(self, path_search_model: bool = True) -> None:

        self._MTI: Final[str] = "1240"
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
        self,
        raw: memoryview,
    ) -> List[Dict[str, Any]]:

        len_raw: int = len(raw)
        index: int = 0
        msg_count: int = 0
        parser_mti: List[Dict[str, Any]] = []
        extract_iso = self._extract_iso_payload
        append_mti = parser_mti.append

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

        return parser_mti

    def file_contents(
        self, date_file: str, cycle: Literal["CIC1", "CIC2", "CIC3"]
    ) -> memoryview:

        _, _, bytes_file = self._path_search_model.get_files_for_cycle(
            date_file=date_file, cycle=cycle
        )

        return bytes_file

    def parse_ipm(self, raw: memoryview) -> List[Dict[str, Any]]:

        return self._playload_ipm_file(
            raw=raw,
        )


if __name__ == "__main__":

    file = MastercardISO8583Parse()

    raw = file.file_contents(date_file="26/05/2025", cycle="CIC2")

    iso = file.parse_ipm(raw=raw)

    # print(iso[1])
