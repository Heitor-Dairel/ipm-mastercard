from datetime import datetime
from typing import Union


class ParseInteger:
    def __init__(self) -> None: ...

    def field(self, data_element: str, name: str) -> Union[int, float]:
        if name == "DE004":
            return int(data_element) / 100

        return int(data_element)


class ParseStringDb:
    def __init__(self) -> None: ...

    def field(self, data_element: str, name: str, custom: bool = False) -> str:
        if custom and name == "DE063":
            return data_element[:3]

        if custom and name == "PDS0158":
            return data_element[:2]

        return data_element


class ParseDate:
    def __init__(self) -> None: ...

    def field(self, data_element: str, name: str) -> str:

        if name == "DE012":
            return datetime.strptime(data_element, "%y%m%d%H%M%S").strftime(
                "%d/%m/%Y %H:%M:%S"
            )

        return datetime.strptime(data_element, "%y%m").strftime("%y/%m")
