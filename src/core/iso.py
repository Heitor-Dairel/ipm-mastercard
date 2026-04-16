from typing import List, Tuple, Dict, Any, Literal, Optional, Union
from ..helpers import file_search, FilesDataSaving, TupleManagerFile
from ..template import mastercard
from ..util import print_custom_text
from starkbank import iso8583
from datetime import datetime


type ParseDb = List[List[Union[int, str, float, None]]]


class ISO8583ParseError(Exception): ...


class MastercardISO8583Parse(FilesDataSaving):

    def __init__(self) -> None:
        super().__init__()

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

    def _playload_ipm_file(self, raw: memoryview) -> Tuple[List[Dict[str, Any]], int]:

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

        return parse_mti, msg_count

    def _logging(
        self, file_name: str, row_count: int, data: List[Dict[str, Any]]
    ) -> None:

        separator: str = "=" * 63

        body: str = (
            f"{separator}\n"
            f" - FILE NAME: {file_name}\n"
            f" - ROW COUNT: {row_count}\n"
            f"{separator}\n"
        )

        self._save_txt(data=data, file_name=file_name)

        print_custom_text(text=body, highlight=["Bold"], color_foreground="OrangeRed1")

    def parse_ipm(
        self,
        date_file: str,
        cycle: Literal["CIC1", "CIC2", "CIC3"],
        logging: bool = True,
    ) -> Optional[Tuple[List[Dict[str, Any]], str]]:

        file_infos: Optional[TupleManagerFile] = file_search(
            file_date=date_file, cycle=cycle
        )

        if file_infos:
            file_name, bytes_file = file_infos
            parse_ipm, msg_count = self._playload_ipm_file(raw=bytes_file)
            if logging:
                self._logging(file_name=file_name, row_count=msg_count, data=parse_ipm)

            return parse_ipm, file_name

        return None

    def parse_ipm_db(
        self,
        date_file: str,
        cycle: Literal["CIC1", "CIC2", "CIC3"],
        logging: bool = True,
    ) -> Optional[Tuple[ParseDb, str]]:

        file_infos: Optional[TupleManagerFile] = file_search(
            file_date=date_file, cycle=cycle
        )

        list_files: ParseDb = []

        if file_infos:
            file_name, bytes_file = file_infos
            parse_ipm, msg_count = self._playload_ipm_file(raw=bytes_file)
            if logging:
                self._logging(file_name=file_name, row_count=msg_count, data=parse_ipm)

            for i in parse_ipm:

                if i["MTI"] == "1240":

                    list_files.append(
                        [
                            i["MTI"],
                            i["DE002"],
                            i["DE003"],
                            int(i["DE004"]) / 100,
                            datetime.strptime(i["DE012"], "%y%m%d%H%M%S").strftime(
                                "%d/%m/%Y %H:%M:%S"
                            ),
                            datetime.strptime(i["DE014"], "%y%m").strftime("%y/%m"),
                            i["DE022"],
                            i["DE023"],
                            i["DE024"],
                            i["DE025"],
                            int(i["DE026"]),
                            i["DE031"],
                            i["DE033"],
                            i["DE038"],
                            i.get("DE040"),
                            i["DE041"],
                            i["DE042"],
                            i["DE043"],
                            i["DE049"],
                            i["DE063"].strip(),
                            i["DE093"],
                            i["DE094"],
                            i["PDS"]["PDS0023"].strip(),
                            i["PDS"]["PDS0052"].strip(),
                            i["PDS"]["PDS0148"].strip(),
                            i["PDS"]["PDS0158"].strip(),
                            i["PDS"]["PDS0165"].strip(),
                            i["PDS"]["PDS0170"].strip(),
                            i["PDS"]["PDS0220"],
                            i["PDS"]["PDS0375"],
                            i["DE063"].strip()[:3],
                            i["PDS"]["PDS0158"].strip()[:2],
                        ]
                    )

            return list_files, file_name

        return None


if __name__ == "__main__":

    file = MastercardISO8583Parse()
    iso = file.parse_ipm(date_file="26/05/2025", cycle="CIC2")

    # print(iso[1])
