"""
biblioteca.py — Núcleo del sistema de biblioteca física.

Contiene:
  - Prestamo   : representa un préstamo activo (composición de Biblioteca).
  - Biblioteca : Singleton que gestiona ejemplares, usuarios y préstamos.
"""

from datetime import date, timedelta
from modelos import Ejemplar, EjemplarPrestable, EjemplarConsulta, Usuario
from utils import ValidarMayuscula, log_operacion


# ─────────────────────────────────────────────
# PRESTAMO
# ─────────────────────────────────────────────

class Prestamo(metaclass=ValidarMayuscula):
    """
    Registra el préstamo de un EjemplarPrestable a un Usuario.

    Composición: Biblioteca crea y destruye estos objetos.
    Un Prestamo no tiene sentido fuera de la Biblioteca.

    Atributos:
        ejemplar       : EjemplarPrestable físico prestado.
        usuario        : Usuario que lleva el ejemplar.
        fecha_inicio   : date de cuando se registró el préstamo.
        fecha_limite   : date hasta la que debe devolverse.
        fecha_devol    : date real de devolución (None si sigue activo).
    """

    def __init__(self, ejemplar: EjemplarPrestable, usuario: Usuario):
        self.ejemplar = ejemplar
        self.usuario = usuario
        self.fecha_inicio: date = date.today()
        self.fecha_limite: date = self.fecha_inicio + timedelta(days=ejemplar.dias_prestamo)
        self.fecha_devol: date | None = None

    @property
    def activo(self) -> bool:
        return self.fecha_devol is None

    @property
    def vencido(self) -> bool:
        return self.activo and date.today() > self.fecha_limite

    def registrar_devolucion(self):
        self.fecha_devol = date.today()

    def __str__(self):
        estado = "ACTIVO" if self.activo else f"DEVUELTO {self.fecha_devol}"
        vencido = " ⚠ VENCIDO" if self.vencido else ""
        return (
            f"Préstamo [{self.ejemplar.id_ejemplar}] "
            f"'{self.ejemplar.titulo}' → {self.usuario.nombre} | "
            f"Límite: {self.fecha_limite} | {estado}{vencido}"
        )

    def __repr__(self):
        return (
            f"Prestamo(id={self.ejemplar.id_ejemplar!r}, "
            f"usuario={self.usuario.legajo!r}, activo={self.activo})"
        )


# ─────────────────────────────────────────────
# BIBLIOTECA  (Singleton)
# ─────────────────────────────────────────────

class Biblioteca(metaclass=ValidarMayuscula):
    """
    Sistema central de la biblioteca física. Patrón Singleton.

    Una sola instancia garantiza que el catálogo de ejemplares,
    los usuarios registrados y los préstamos sean siempre consistentes,
    sin importar desde qué parte del código se acceda.

    Relaciones:
        Agregación  → listas de Ejemplar y Usuario
                      (existen independientemente de la Biblioteca).
        Composición → lista de Prestamo
                      (los préstamos son creados y destruidos por Biblioteca).
    """

    _instancia = None   # única instancia compartida por todo el sistema

    # ── Singleton ──────────────────────────────
    def __new__(cls, nombre: str = "Biblioteca Central"):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            # Inicializar atributos solo la primera vez
            cls._instancia._inicializada = False
        return cls._instancia

    def __init__(self, nombre: str = "Biblioteca Central"):
        # __init__ se ejecuta cada vez que se llama a Biblioteca(),
        # pero los datos solo se cargan la primera vez.
        if self._inicializada:
            return
        self.nombre = nombre
        self._ejemplares: list[Ejemplar] = []    # agregación
        self._usuarios: list[Usuario] = []        # agregación
        self._prestamos: list[Prestamo] = []      # composición
        self._inicializada = True

    # ── Representación ─────────────────────────
    def __str__(self):
        return (
            f"=== {self.nombre} ===\n"
            f"  Ejemplares : {len(self._ejemplares)}\n"
            f"  Usuarios   : {len(self._usuarios)}\n"
            f"  Préstamos activos : "
            f"{sum(1 for p in self._prestamos if p.activo)}"
        )

    # ══════════════════════════════════════════
    # GESTIÓN DE EJEMPLARES
    # ══════════════════════════════════════════

    @log_operacion
    def registrar_ejemplar(self, ejemplar: Ejemplar) -> str:
        """Alta de un ejemplar físico en el catálogo."""
        if self._buscar_ejemplar_por_id(ejemplar.id_ejemplar):
            raise ValueError(
                f"Ya existe un ejemplar con ID '{ejemplar.id_ejemplar}'."
            )
        self._ejemplares.append(ejemplar)
        return f"Ejemplar '{ejemplar.id_ejemplar}' registrado."

    @log_operacion
    def dar_baja_ejemplar(self, id_ejemplar: str) -> str:
        """Baja de un ejemplar (solo si no está prestado)."""
        ej = self._buscar_ejemplar_por_id(id_ejemplar)
        if not ej:
            raise ValueError(f"No se encontró el ejemplar '{id_ejemplar}'.")
        if isinstance(ej, EjemplarPrestable) and not ej.disponible:
            raise ValueError(
                f"No se puede dar de baja '{id_ejemplar}': está prestado."
            )
        self._ejemplares.remove(ej)
        return f"Ejemplar '{id_ejemplar}' dado de baja."

    def listar_ejemplares(self):
        """Imprime el catálogo completo con detalles de cada ejemplar."""
        if not self._ejemplares:
            print("  (catálogo vacío)")
            return
        for ej in self._ejemplares:
            print(ej.mostrar_detalles())   # polimorfismo en acción
            print()

    # ══════════════════════════════════════════
    # GESTIÓN DE USUARIOS
    # ══════════════════════════════════════════

    @log_operacion
    def registrar_usuario(self, usuario: Usuario) -> str:
        """Alta de un usuario en el sistema."""
        if self._buscar_usuario_por_legajo(usuario.legajo):
            raise ValueError(
                f"Ya existe un usuario con legajo '{usuario.legajo}'."
            )
        self._usuarios.append(usuario)
        return f"Usuario '{usuario.nombre}' registrado."

    @log_operacion
    def dar_baja_usuario(self, legajo: str) -> str:
        """Baja de un usuario (solo si no tiene préstamos activos)."""
        u = self._buscar_usuario_por_legajo(legajo)
        if not u:
            raise ValueError(f"No se encontró el usuario '{legajo}'.")
        if u.prestamos_activos:
            raise ValueError(
                f"No se puede dar de baja '{legajo}': "
                f"tiene {len(u.prestamos_activos)} préstamo(s) activo(s)."
            )
        self._usuarios.remove(u)
        return f"Usuario '{u.nombre}' dado de baja."

    def listar_usuarios(self):
        """Imprime todos los usuarios registrados."""
        if not self._usuarios:
            print("  (sin usuarios registrados)")
            return
        for u in self._usuarios:
            print(u)

    # ══════════════════════════════════════════
    # GESTIÓN DE PRÉSTAMOS  (composición)
    # ══════════════════════════════════════════

    @log_operacion
    def prestar_ejemplar(self, id_ejemplar: str, legajo: str) -> str:
        """
        Registra el préstamo de un EjemplarPrestable a un Usuario.
        Biblioteca crea el objeto Prestamo → composición.
        """
        ej = self._buscar_ejemplar_por_id(id_ejemplar)
        if not ej:
            raise ValueError(f"Ejemplar '{id_ejemplar}' no encontrado.")
        if isinstance(ej, EjemplarConsulta):
            raise ValueError(
                f"'{id_ejemplar}' es de consulta en sala. No se presta."
            )
        u = self._buscar_usuario_por_legajo(legajo)
        if not u:
            raise ValueError(f"Usuario '{legajo}' no encontrado.")
        if not ej.disponible:
            raise ValueError(
                f"'{id_ejemplar}' no está disponible (estado: {ej.estado})."
            )

        # Composición: Biblioteca crea el Prestamo
        prestamo = Prestamo(ej, u)
        ej.estado = "prestado"
        u.prestamos_activos.append(prestamo)
        self._prestamos.append(prestamo)
        return (
            f"Préstamo registrado: '{ej.titulo}' → {u.nombre} "
            f"(devolver antes del {prestamo.fecha_limite})."
        )

    @log_operacion
    def devolver_ejemplar(self, id_ejemplar: str) -> str:
        """Registra la devolución de un ejemplar prestado."""
        prestamo = self._buscar_prestamo_activo(id_ejemplar)
        if not prestamo:
            raise ValueError(
                f"No hay préstamo activo para el ejemplar '{id_ejemplar}'."
            )
        prestamo.registrar_devolucion()
        prestamo.ejemplar.estado = "disponible"
        prestamo.usuario.prestamos_activos.remove(prestamo)
        return (
            f"Devolución registrada: '{prestamo.ejemplar.titulo}' "
            f"— devuelto por {prestamo.usuario.nombre}."
        )

    def listar_prestamos(self, solo_activos: bool = True):
        """Imprime préstamos activos (o todos si solo_activos=False)."""
        lista = [p for p in self._prestamos if p.activo] if solo_activos else self._prestamos
        if not lista:
            print("  (sin préstamos)")
            return
        for p in lista:
            print(p)

    # ══════════════════════════════════════════
    # BÚSQUEDAS INTERNAS (helpers privados)
    # ══════════════════════════════════════════

    def _buscar_ejemplar_por_id(self, id_ejemplar: str) -> Ejemplar | None:
        return next(
            (e for e in self._ejemplares if e.id_ejemplar == id_ejemplar),
            None,
        )

    def _buscar_usuario_por_legajo(self, legajo: str) -> Usuario | None:
        return next(
            (u for u in self._usuarios if u.legajo == legajo),
            None,
        )

    def _buscar_prestamo_activo(self, id_ejemplar: str) -> Prestamo | None:
        return next(
            (p for p in self._prestamos if p.activo and p.ejemplar.id_ejemplar == id_ejemplar),
            None,
        )
