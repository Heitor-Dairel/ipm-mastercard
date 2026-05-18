import timeit

from src.core import MC8583

master = MC8583()

master.search_ipm(file_date="26/05/2025", cycle="CIC2")


def fun_to_teste():

    _ = master.parse_ipm()


time_exec = 6
result = timeit.timeit(fun_to_teste, number=time_exec)


print(f"Tempo para {time_exec} execuções: {result:.4f} s")
print(f"Tempo médio: {result / time_exec:.6f} s")
