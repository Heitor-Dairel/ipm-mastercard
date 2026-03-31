from typing import List, Dict, Any
from src.core import MastercardISO8583Parse

data: List[Dict[str, Any]] = []

datas = "25/02/2025"

retirar = ["DE048", "DE055"]

file = MastercardISO8583Parse()

file_name, raw = file.file_contents(date_file=datas, cycle="CIC1")

iso = file.parse_ipm(raw=raw)

file.output_excel(parse=iso, field=retirar)
