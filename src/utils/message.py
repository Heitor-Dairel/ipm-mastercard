from typing import Any, Dict, Final, List, Optional

from ..models import TypeElementsIpm, TypeIpm, TypeIpmDb
from ..template import FieldDb, TemplateDb


class BeautifyIpmDb:
    _DATA_ELEMENTS_MESSAGE: Final[TypeElementsIpm] = [
        ["MTI", "DE"],
        ["DE002", "DE"],
        ["DE003", "DE"],
        ["DE004", "DE"],
        ["DE012", "DE"],
        ["DE014", "DE"],
        ["DE022", "DE"],
        ["DE023", "DE"],
        ["DE024", "DE"],
        ["DE025", "DE"],
        ["DE026", "DE"],
        ["DE031", "DE"],
        ["DE033", "DE"],
        ["DE038", "DE"],
        ["DE040", "DE"],
        ["DE041", "DE"],
        ["DE042", "DE"],
        ["DE043", "DE"],
        ["DE049", "DE"],
        ["DE063", "DE"],
        ["DE093", "DE"],
        ["DE094", "DE"],
        ["PDS0023", "PDS"],
        ["PDS0052", "PDS"],
        ["PDS0148", "PDS"],
        ["PDS0158", "PDS"],
        ["PDS0165", "PDS"],
        ["PDS0170", "PDS"],
        ["PDS0220", "PDS"],
        ["PDS0375", "PDS"],
        ["DE063", "DE"],
        ["PDS0158", "PDS"],
    ]

    def __init__(self, template: TemplateDb, elements: TypeIpm) -> None:
        self.elements: TypeIpm = elements
        self.template = template

    def parse(
        self,
    ) -> List[List[TypeIpmDb]]:

        parse_db: List[List[TypeIpmDb]] = []
        parse_db_append = parse_db.append

        for message in self.elements:
            if message["MTI"] == "1240":
                parse_db_append(self._loop_element(message=message))

        return parse_db

    def _loop_element(
        self,
        message: Dict[str, Any],
    ) -> List[TypeIpmDb]:

        key: Optional[str] = None
        value: Optional[str] = None
        data_element: Optional[TypeIpmDb] = None
        parse_elements: List[TypeIpmDb] = []
        parse_elements_append = parse_elements.append

        for element in self._DATA_ELEMENTS_MESSAGE:
            key = element[1]
            value = element[0]
            data_element = self._get_element(
                message=message, name=value, type_element=key
            )

            parse_elements_append(data_element)

        return parse_elements

    def _get_element(
        self,
        message: Dict[str, Any],
        name: str,
        type_element: str,
    ) -> TypeIpmDb:

        data_element: Optional[str] = None
        element_ipm: Optional[FieldDb] = None

        if type_element == "DE":
            data_element = message.get(name)

        if type_element == "PDS":
            data_element = message[type_element].get(name)

        if data_element:
            element_ipm = self.template.get_field(name=name)
            return element_ipm.parsing(data_element=data_element.strip())

        return data_element
