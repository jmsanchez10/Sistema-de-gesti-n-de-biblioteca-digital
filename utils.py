"""
utils.py — Componentes técnicos transversales del sistema.
"""
from datetime import datetime
import functools

class ValidarMayuscula(type):
    def __new__(mcs, nombre, bases, namespace):
        if not nombre[0].isupper():
            raise TypeError(f"El nombre de clase '{nombre}' debe comenzar con mayúscula.")
        return super().__new__(mcs, nombre, bases, namespace)

def log_operacion(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        args_str = ", ".join(str(a) for a in args[1:])
        print(f"[{timestamp}] OPERACIÓN › {func.__name__}({args_str})")
        try:
            resultado = func(*args, **kwargs)
            print(f"[{timestamp}]    ✔ resultado: {resultado}")
            return resultado
        except Exception as e:
            print(f"[{timestamp}]    ✘ error: {e}")
            raise
    return wrapper
