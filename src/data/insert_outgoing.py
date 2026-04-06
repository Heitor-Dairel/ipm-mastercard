from ..core import MastercardISO8583Parse
from typing import Optional
from dotenv import load_dotenv
from rich import print
from datetime import datetime
import os

load_dotenv()

host: Optional[str] = os.getenv("DB_HOST")
port: Optional[str] = os.getenv("DB_PORT")
db_name: Optional[str] = os.getenv("DB_NAME")
user: Optional[str] = os.getenv("DB_USERNAME")
password: Optional[str] = os.getenv("DB_PASSWORD")


# print(host, port, db_name, user, password)


file = MastercardISO8583Parse()

arq_parse = file.parse_ipm(date_file="25/03/2026", cycle="CIC1")

if arq_parse:
    print(arq_parse[1])
    print(f"{arq_parse[1]["MTI"]=}")
    print(f"{arq_parse[1]["DE002"]=}")
    print(int(arq_parse[1]["DE004"]) / 100)
    print(
        datetime.strptime(arq_parse[1]["DE012"], "%y%m%d%H%M%S").strftime(
            "%d/%m/%Y %H:%M:%S"
        )
    )
    print(f"{arq_parse[1]['DE014']=}")
    print(f"{arq_parse[1]['DE022']=}")
    print(f"{arq_parse[1]['DE023']=}")
    print(f"{arq_parse[1]['DE024']=}")
    print(f"{arq_parse[1]['DE025']=}")
    print(f"{arq_parse[1]['DE026']=}")
    print(f"{arq_parse[1]['DE031']=}")
    print(f"{arq_parse[1]['DE033']=}")
    print(f"{arq_parse[1]['DE038']=}")
    print(f"{arq_parse[1]['DE040']=}")
    print(f"{arq_parse[1]['DE041']=}")
    print(f"{arq_parse[1]['DE042']=}")
    print(f"{arq_parse[1]['DE043']=}")
    print(f"{arq_parse[1]['DE049']=}")
    print(f"{arq_parse[1]['DE063'].strip()=}")
    print(f"{arq_parse[1]['DE071']=}")
    print(f"{arq_parse[1]['DE093']=}")
    print(f"{arq_parse[1]['DE094']=}")
    print(f"arq_parse[1][PDS][PDS0158]={arq_parse[1]["PDS"]["PDS0158"].strip()[:2]}")


"a".strip
