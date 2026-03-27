from src.core import MastercardISO8583Parse
from rich import print
import timeit

file = MastercardISO8583Parse()


def fun_to_teste():

    teste, _ = file.parse_ipm(date_file="26/05/2025", cycle="CIC2")


time_exec = 10
result = timeit.timeit(fun_to_teste, number=time_exec)


print(f"Tempo para {time_exec} execuções: {result:.4f} s")
print(f"Tempo médio: {result / time_exec * 1:.6f} ms")
