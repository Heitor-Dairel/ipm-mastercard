from src.data import DB8583

with DB8583() as db:
    db.iso_db(date_file="26/05/2025", cycle="CIC2")
