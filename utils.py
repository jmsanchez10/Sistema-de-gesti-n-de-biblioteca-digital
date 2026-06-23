"""
utils.py — Componentes técnicos transversales del sistema.

Contiene:
  - ValidarMayuscula : metaclase que garantiza nombres de clase con mayúscula inicial.
  - log_operacion    : decorador que registra en consola cada alta/baja/préstamo.
"""

from datetime import datetime
import functools


# ─────────────────────────────────────────────
# METACLASE
# ─────────────────────────────────────────────

class ValidarMayuscula(type):
    """
    Metaclase basada en 'type'.

    Intercepta la creación de cada clase que la declare como metaclase
    y lanza un TypeError si el nombre no empieza con mayúscula.

    Uso:
        class MiClase(metaclass=ValidarMayuscula): ...   # OK
        class miClase(metaclass=ValidarMayuscula): ...   # TypeError
    """

    def __new__(mcs, nombre, bases, namespace):
        if not nombre[0].isupper():
            raise TypeError(
                f"El nombre de clase '{nombre}' debe comenzar con mayúscula."
            )
        return super().__new__(mcs, nombre, bases, namespace)


# ─────────────────────────────────────────────
# DECORADOR
# ─────────────────────────────────────────────

def log_operacion(func):
    """
    Decorador propio que imprime en consola cada vez que se ejecuta
    una operación relevante del sistema (alta, baja, préstamo, devolución).

    Registra:
      - Fecha y hora de la operación.
      - Nombre del método ejecutado.
      - Argumentos recibidos (excluyendo 'self').
      - Resultado devuelto por el método.
      - Cualquier excepción que se produzca.

    Uso:
        @log_operacion
        def registrar_ejemplar(self, ejemplar): ...
    """

    @functools.wraps(func)  # preserva nombre y docstring del método original
    def wrapper(*args, **kwargs):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # args[0] es 'self'; los demás son los argumentos reales
        args_str = ", ".join(str(a) for a in args[1:])
        print(f"[{timestamp}] OPERACIÓN › {func.__name__}({args_str})")
        try:
            resultado = func(*args, **kwargs)
            print(f"[{timestamp}]    ✔ resultado: {resultado}")
            return resultado
        except Exception as e:
            print(f"[{timestamp}]    ✘ error: {e}")
            raise  # re-lanza la excepción para no ocultar el error

    return wrapper
