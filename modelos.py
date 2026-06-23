"""
modelos.py — Clases de dominio del sistema de biblioteca física.

Jerarquía:
  Persona (base)
    └── Usuario

  Ejemplar (base)
    ├── EjemplarPrestable   → se puede llevar a casa
    └── EjemplarConsulta    → solo lectura en sala

Todas usan ValidarMayuscula como metaclase.
El polimorfismo se expresa en mostrar_detalles().
"""

from utils import ValidarMayuscula


# ─────────────────────────────────────────────
# PERSONA y USUARIO
# ─────────────────────────────────────────────

class Persona(metaclass=ValidarMayuscula):
    """Clase base que representa a cualquier persona del sistema."""

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
    """
    Persona habilitada para interactuar con la biblioteca.
    Hereda de Persona y agrega email y lista de préstamos activos.
    """

    def __init__(self, nombre: str, apellido: str, dni: str, email: str):
        super().__init__(nombre, apellido, dni)
        self.email = email
        self.prestamos_activos: list = []   # lista de objetos Prestamo

    def __str__(self):
        return (
            f"{self.nombre_completo} | DNI: {self.dni} | "
            f"Email: {self.email} | "
            f"Préstamos activos: {len(self.prestamos_activos)}"
        )

    def __repr__(self):
        return f"Usuario(dni={self.dni!r}, nombre={self.nombre_completo!r})"


# ─────────────────────────────────────────────
# EJEMPLAR (clase base)
# ─────────────────────────────────────────────

class Ejemplar(metaclass=ValidarMayuscula):
    """
    Representa un ejemplar físico concreto en las estanterías.

    Un mismo ISBN puede tener varios ejemplares, cada uno con su
    propio id_ejemplar (código de barra o ID único).
    """

    def __init__(
        self,
        id_ejemplar: str,
        titulo: str,
        autor: str,
        isbn: str,
        anio_publicacion: int,
        cantidad_paginas: int,
    ):
        self.id_ejemplar = id_ejemplar       # código de barra único
        self.titulo = titulo
        self.autor = autor
        self.isbn = isbn
        self.anio_publicacion = anio_publicacion
        self.cantidad_paginas = cantidad_paginas

    def mostrar_detalles(self) -> str:
        """
        Método polimórfico: cada subclase lo implementa a su manera.
        En la clase base devuelve solo los datos comunes.
        """
        return (
            f"[{self.id_ejemplar}] '{self.titulo}' — {self.autor} | "
            f"ISBN: {self.isbn} | Año: {self.anio_publicacion} | "
            f"Páginas: {self.cantidad_paginas}"
        )

    def __str__(self):
        return self.mostrar_detalles()

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"id={self.id_ejemplar!r}, titulo={self.titulo!r})"
        )


# ─────────────────────────────────────────────
# SUBCLASE 1: EjemplarPrestable
# ─────────────────────────────────────────────

ESTADOS_VALIDOS = {"disponible", "prestado", "reservado"}


class EjemplarPrestable(Ejemplar):
    """
    Ejemplar que puede salir de la biblioteca (préstamo a domicilio).

    Agrega:
      - estado        : 'disponible' | 'prestado' | 'reservado'
      - dias_prestamo : cuántos días se permite tenerlo fuera
    """

    def __init__(
        self,
        id_ejemplar: str,
        titulo: str,
        autor: str,
        isbn: str,
        anio_publicacion: int,
        cantidad_paginas: int,
        dias_prestamo: int = 7,
    ):
        super().__init__(id_ejemplar, titulo, autor, isbn,
                         anio_publicacion, cantidad_paginas)
        self._estado = "disponible"
        self.dias_prestamo = dias_prestamo

    # ── propiedad con validación de estado ──
    @property
    def estado(self) -> str:
        return self._estado

    @estado.setter
    def estado(self, nuevo: str):
        if nuevo not in ESTADOS_VALIDOS:
            raise ValueError(
                f"Estado inválido: '{nuevo}'. "
                f"Opciones: {ESTADOS_VALIDOS}"
            )
        self._estado = nuevo

    @property
    def disponible(self) -> bool:
        return self._estado == "disponible"

    def mostrar_detalles(self) -> str:
        """Polimorfismo: muestra estado y plazo de préstamo."""
        base = super().mostrar_detalles()
        return (
            f"{base}\n"
            f"   Tipo: PRESTABLE | Estado: {self._estado.upper()} | "
            f"Plazo: {self.dias_prestamo} días"
        )


# ─────────────────────────────────────────────
# SUBCLASE 2: EjemplarConsulta
# ─────────────────────────────────────────────

class EjemplarConsulta(Ejemplar):
    """
    Ejemplar que SOLO puede consultarse dentro de la sala de lectura.
    No puede prestarse bajo ninguna circunstancia.

    Agrega:
      - sala : nombre o número de sala donde se ubica físicamente
    """

    def __init__(
        self,
        id_ejemplar: str,
        titulo: str,
        autor: str,
        isbn: str,
        anio_publicacion: int,
        cantidad_paginas: int,
        sala: str = "Sala general",
    ):
        super().__init__(id_ejemplar, titulo, autor, isbn,
                         anio_publicacion, cantidad_paginas)
        self.sala = sala

    def mostrar_detalles(self) -> str:
        """Polimorfismo: aclara que NO es prestable y dónde consultarlo."""
        base = super().mostrar_detalles()
        return (
            f"{base}\n"
            f"   Tipo: CONSULTA EN SALA | Ubicación: {self.sala} | "
            f"⚠ No se presta"
        )
