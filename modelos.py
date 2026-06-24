"""
modelos.py — Clases de dominio del sistema de biblioteca física.
"""
from utils import ValidarMayuscula

class Persona(metaclass=ValidarMayuscula):
    def __init__(self, nombre: str, apellido: str, dni: str):
        self.nombre = nombre
        self.apellido = apellido
        self.dni = dni

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"

    def __str__(self):
        return f"{self.nombre_completo} (DNI: {self.dni})"

class Usuario(Persona):
    def __init__(self, nombre: str, apellido: str, dni: str, email: str):
        super().__init__(nombre, apellido, dni)
        self.email = email
        self.prestamos_activos: list = []

    def __str__(self):
        return (f"{self.nombre_completo} | DNI: {self.dni} | "
                f"Email: {self.email} | Préstamos activos: {len(self.prestamos_activos)}")

    def __repr__(self):
        return f"Usuario(dni={self.dni!r}, nombre={self.nombre_completo!r})"

ESTADOS_VALIDOS = {"disponible", "prestado", "reservado"}

class Ejemplar(metaclass=ValidarMayuscula):
    def __init__(self, id_ejemplar: str, titulo: str, autor: str, isbn: str,
                 anio_publicacion: int, cantidad_paginas: int):
        self.id_ejemplar = id_ejemplar
        self.titulo = titulo
        self.autor = autor
        self.isbn = isbn
        self.anio_publicacion = anio_publicacion
        self.cantidad_paginas = cantidad_paginas

    def mostrar_detalles(self) -> str:
        return (f"[{self.id_ejemplar}] '{self.titulo}' — {self.autor} | "
                f"ISBN: {self.isbn} | Año: {self.anio_publicacion} | "
                f"Páginas: {self.cantidad_paginas}")

    def __str__(self): return self.mostrar_detalles()
    def __repr__(self): return f"{self.__class__.__name__}(id={self.id_ejemplar!r}, titulo={self.titulo!r})"

class EjemplarPrestable(Ejemplar):
    def __init__(self, id_ejemplar, titulo, autor, isbn, anio_publicacion, cantidad_paginas, dias_prestamo=7):
        super().__init__(id_ejemplar, titulo, autor, isbn, anio_publicacion, cantidad_paginas)
        self._estado = "disponible"
        self.dias_prestamo = dias_prestamo

    @property
    def estado(self): return self._estado

    @estado.setter
    def estado(self, nuevo):
        if nuevo not in ESTADOS_VALIDOS:
            raise ValueError(f"Estado inválido: '{nuevo}'. Opciones: {ESTADOS_VALIDOS}")
        self._estado = nuevo

    @property
    def disponible(self): return self._estado == "disponible"

    def mostrar_detalles(self) -> str:
        base = super().mostrar_detalles()
        return f"{base}\n   Tipo: PRESTABLE | Estado: {self._estado.upper()} | Plazo: {self.dias_prestamo} días"

class EjemplarConsulta(Ejemplar):
    def __init__(self, id_ejemplar, titulo, autor, isbn, anio_publicacion, cantidad_paginas, sala="Sala general"):
        super().__init__(id_ejemplar, titulo, autor, isbn, anio_publicacion, cantidad_paginas)
        self.sala = sala

    def mostrar_detalles(self) -> str:
        base = super().mostrar_detalles()
        return f"{base}\n   Tipo: CONSULTA EN SALA | Ubicación: {self.sala} | ⚠ No se presta"
