from src.core import MastercardISO8583Parse
from rich import print
import timeit


file = MastercardISO8583Parse()

raw = file.file_contents(date_file="26/05/2025", cycle="CIC2")


def fun_to_teste():

    iso, iso2 = file.parse_ipm(raw=raw)


time_exec = 6
result = timeit.timeit(fun_to_teste, number=time_exec)


print(f"Tempo para {time_exec} execuções: {result:.4f} s")
print(f"Tempo médio: {result / time_exec:.6f} s")
