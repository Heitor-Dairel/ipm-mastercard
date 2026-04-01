from typing import List, Dict, Any
from src.core import MastercardISO8583Parse

data: List[Dict[str, Any]] = []

datas = "26/03/2026"

retirar = ["DE048", "DE055"]

file = MastercardISO8583Parse()

iso = file.parse_ipm(date_file=datas, cycle="CIC1")

file.output_excel(parse=iso, field=retirar)
