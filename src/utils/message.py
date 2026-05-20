from copy import deepcopy
from typing import Any, Dict, Final, List, Optional, Tuple

from starkbank.iso8583.template.base import Template
from starkbank.iso8583.utils.bitmap import getBitmapFields, getElementId, isBitmap
from starkbank.iso8583.utils.header import NoHeaderRule
from starkbank.iso8583.utils.pds import breakPdsElement, buildPdsElement

from ..models import TypeIpm, TypeIpmDb
from ..template import FieldDb, TemplateDb
from .version import IsoVersion


def get_version(mti: str) -> str:
    VERSION_MAP: Final[Dict[str, str]] = {
        "0": IsoVersion.ISO1987,
        "1": IsoVersion.ISO1993,
    }
    try:
        return VERSION_MAP[mti[0]]
    except KeyError:
        raise ValueError(
            "Expected '0' or '1' in MTI[0] (Actual: {mti}), please check iso8583.encoding".format(
                mti=mti
            )
        )


def iso_parse(
    message: bytes,
    template: Dict[str, Template],
    encoding: Optional[str],
) -> Dict[str, Any]:
    json, template_current = {}, template
    header_rule: Optional[NoHeaderRule] = template_current[
        IsoVersion.ISO1987
    ].get_header_rule()
    if header_rule:
        message, json = header_rule.parse(data=message, json=json)

    MTI, message, length = parseElement(
        message,
        element_id="MTI",
        template=template_current[IsoVersion.ISO1987],
        encoding=encoding,
    )
    version: str = get_version(mti=MTI)

    result, message, length = loopMessage(
        message, length, template_current[version], encoding=encoding
    )
    json.update(MTI=MTI, BMP=result.pop("DE000"))
    json.update(result)
    if version == IsoVersion.ISO1993:
        json = buildPdsElement(json=json)
    json["Length"] = length
    return json


def iso_unparse(
    parsed: Dict[str, Any],
    template: Dict[str, Template],
    encoding: Optional[str] = None,
) -> bytes:
    template_current: Dict[str, Template] = template
    parsed_current: Dict[str, Any] = deepcopy(parsed)
    output: bytes = b""

    version: str = get_version(mti=parsed_current["MTI"])
    if version == IsoVersion.ISO1993:
        parsed_current = breakPdsElement(json=parsed_current)

    parsed_current.update(getBitmapFields(json=parsed_current))
    element_ids: List[str] = sorted(key for key in parsed_current if "DE" in key)

    output += unparseElement(
        parsed_current,
        element_id="MTI",
        template=template_current[version],
        encoding=encoding,
    )
    for id in element_ids:
        output += unparseElement(
            parsed_current,
            element_id=id,
            template=template_current[version],
            encoding=encoding,
        )

    headerRule: Optional[NoHeaderRule] = template_current[
        IsoVersion.ISO1987
    ].get_header_rule()
    if headerRule:
        output = headerRule.unparse(data=output, json=parsed_current) + output
    return output


def loopMessage(
    message: Any, length: int, template: Template, encoding: Optional[str]
) -> Tuple[Any, ...]:
    result = {}
    indexes = [0]
    for number in indexes:
        id = getElementId(number)
        value, message, parsedLength = parseElement(
            message=message, element_id=id, template=template, encoding=encoding
        )
        length += parsedLength
        result[id] = value
        if isBitmap(id):
            indexes.extend(value)
    return result, message, length


def parseElement(
    message: bytes, element_id: str, template: Template, encoding: Optional[str]
) -> Any:
    field = template.get_field(element_id)
    return field.parse(data=message, encoding=encoding)


def unparseElement(
    parsed: Dict[str, Any], element_id: str, template: Template, encoding: Optional[Any]
) -> Any:
    field = template.get_field(element_id)
    return field.unparse(value=parsed[element_id], encoding=encoding)


class BeautifyIpmDb:
    _DATA_ELEMENTS_MESSAGE: Final[List[List[str]]] = [
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

    def iso_parse(
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

        parse_elements: List[TypeIpmDb] = []
        parse_elements_append = parse_elements.append

        for element in self._DATA_ELEMENTS_MESSAGE:
            key: str = element[1]
            value: str = element[0]
            data_element: TypeIpmDb = self._get_element(
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

        if type_element == "DE":
            data_element = message.get(name)

        if type_element == "PDS":
            data_element = message[type_element].get(name)

        if data_element:
            element_ipm: FieldDb = self.template.get_field(name=name)
            return element_ipm.parsing(data_element=data_element.strip())

        return data_element
