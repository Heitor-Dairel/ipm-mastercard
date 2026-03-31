from src.core import MastercardISO8583Parse
from rich import print

file = MastercardISO8583Parse()

raw = file.file_contents(date_file="26/05/2025", cycle="CIC2")

iso = file.parse_ipm(raw=raw)

print(iso[0])
