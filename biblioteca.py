"""
biblioteca.py — Núcleo del sistema de biblioteca física.
"""
from datetime import date, timedelta
from modelos import Ejemplar, EjemplarPrestable, EjemplarConsulta, Usuario
from utils import ValidarMayuscula, log_operacion

class Prestamo(metaclass=ValidarMayuscula):
    def __init__(self, ejemplar: EjemplarPrestable, usuario: Usuario):
        self.ejemplar = ejemplar
        self.usuario = usuario
        self.fecha_inicio: date = date.today()
        self.fecha_limite: date = self.fecha_inicio + timedelta(days=ejemplar.dias_prestamo)
        self.fecha_devol: date | None = None

    @property
    def activo(self): return self.fecha_devol is None

    @property
    def vencido(self): return self.activo and date.today() > self.fecha_limite

    def registrar_devolucion(self): self.fecha_devol = date.today()

    def __str__(self):
        estado = "ACTIVO" if self.activo else f"DEVUELTO {self.fecha_devol}"
        vencido = " ⚠ VENCIDO" if self.vencido else ""
        return (f"Préstamo [{self.ejemplar.id_ejemplar}] '{self.ejemplar.titulo}' "
                f"→ {self.usuario.nombre_completo} | Límite: {self.fecha_limite} | {estado}{vencido}")

    def __repr__(self):
        return f"Prestamo(id={self.ejemplar.id_ejemplar!r}, usuario={self.usuario.dni!r}, activo={self.activo})"

class Biblioteca(metaclass=ValidarMayuscula):
    _instancia = None

    def __new__(cls, nombre="Biblioteca Central"):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializada = False
        return cls._instancia

    def __init__(self, nombre="Biblioteca Central"):
        if self._inicializada: return
        self.nombre = nombre
        self._ejemplares: list[Ejemplar] = []
        self._usuarios: list[Usuario] = []
        self._prestamos: list[Prestamo] = []
        self._inicializada = True

    def __str__(self):
        return (f"=== {self.nombre} ===\n  Ejemplares : {len(self._ejemplares)}\n"
                f"  Usuarios   : {len(self._usuarios)}\n"
                f"  Préstamos activos : {sum(1 for p in self._prestamos if p.activo)}")

    @log_operacion
    def registrar_ejemplar(self, ejemplar: Ejemplar) -> str:
        if self._buscar_ejemplar_por_id(ejemplar.id_ejemplar):
            raise ValueError(f"Ya existe un ejemplar con ID '{ejemplar.id_ejemplar}'.")
        self._ejemplares.append(ejemplar)
        return f"Ejemplar '{ejemplar.id_ejemplar}' registrado."

    @log_operacion
    def modificar_ejemplar(self, id_ejemplar, titulo=None, autor=None, isbn=None,
                           anio_publicacion=None, cantidad_paginas=None,
                           dias_prestamo=None, sala=None) -> str:
        ej = self._buscar_ejemplar_por_id(id_ejemplar)
        if not ej: raise ValueError(f"No se encontró el ejemplar '{id_ejemplar}'.")
        if titulo:           ej.titulo = titulo
        if autor:            ej.autor = autor
        if isbn:             ej.isbn = isbn
        if anio_publicacion: ej.anio_publicacion = anio_publicacion
        if cantidad_paginas: ej.cantidad_paginas = cantidad_paginas
        if dias_prestamo and isinstance(ej, EjemplarPrestable): ej.dias_prestamo = dias_prestamo
        if sala and isinstance(ej, EjemplarConsulta): ej.sala = sala
        return f"Ejemplar '{id_ejemplar}' modificado."

    @log_operacion
    def dar_baja_ejemplar(self, id_ejemplar: str) -> str:
        ej = self._buscar_ejemplar_por_id(id_ejemplar)
        if not ej: raise ValueError(f"No se encontró el ejemplar '{id_ejemplar}'.")
        if isinstance(ej, EjemplarPrestable) and not ej.disponible:
            raise ValueError(f"No se puede dar de baja '{id_ejemplar}': está prestado.")
        self._ejemplares.remove(ej)
        return f"Ejemplar '{id_ejemplar}' dado de baja."

    def listar_ejemplares(self):
        if not self._ejemplares: print("  (catálogo vacío)"); return
        for ej in self._ejemplares: print(ej.mostrar_detalles()); print()

    @log_operacion
    def registrar_usuario(self, usuario: Usuario) -> str:
        if self._buscar_usuario_por_dni(usuario.dni):
            raise ValueError(f"Ya existe un usuario con DNI '{usuario.dni}'.")
        self._usuarios.append(usuario)
        return f"Usuario '{usuario.nombre_completo}' registrado."

    @log_operacion
    def modificar_usuario(self, dni, nombre=None, apellido=None, email=None) -> str:
        u = self._buscar_usuario_por_dni(dni)
        if not u: raise ValueError(f"No se encontró el usuario con DNI '{dni}'.")
        if nombre:   u.nombre = nombre
        if apellido: u.apellido = apellido
        if email:    u.email = email
        return f"Usuario '{u.nombre_completo}' modificado."

    @log_operacion
    def dar_baja_usuario(self, dni: str) -> str:
        u = self._buscar_usuario_por_dni(dni)
        if not u: raise ValueError(f"No se encontró el usuario con DNI '{dni}'.")
        if u.prestamos_activos:
            raise ValueError(f"No se puede dar de baja '{dni}': tiene {len(u.prestamos_activos)} préstamo(s) activo(s).")
        self._usuarios.remove(u)
        return f"Usuario '{u.nombre_completo}' dado de baja."

    def listar_usuarios(self):
        if not self._usuarios: print("  (sin usuarios registrados)"); return
        for u in self._usuarios: print(u)

    @log_operacion
    def prestar_ejemplar(self, id_ejemplar: str, dni: str) -> str:
        ej = self._buscar_ejemplar_por_id(id_ejemplar)
        if not ej: raise ValueError(f"Ejemplar '{id_ejemplar}' no encontrado.")
        if isinstance(ej, EjemplarConsulta):
            raise ValueError(f"'{id_ejemplar}' es de consulta en sala. No se presta.")
        u = self._buscar_usuario_por_dni(dni)
        if not u: raise ValueError(f"Usuario con DNI '{dni}' no encontrado.")
        if not ej.disponible:
            raise ValueError(f"'{id_ejemplar}' no está disponible (estado: {ej.estado}).")
        prestamo = Prestamo(ej, u)
        ej.estado = "prestado"
        u.prestamos_activos.append(prestamo)
        self._prestamos.append(prestamo)
        return f"Préstamo registrado: '{ej.titulo}' → {u.nombre_completo} (devolver antes del {prestamo.fecha_limite})."

    @log_operacion
    def devolver_ejemplar(self, id_ejemplar: str) -> str:
        prestamo = self._buscar_prestamo_activo(id_ejemplar)
        if not prestamo:
            raise ValueError(f"No hay préstamo activo para el ejemplar '{id_ejemplar}'.")
        prestamo.registrar_devolucion()
        prestamo.ejemplar.estado = "disponible"
        prestamo.usuario.prestamos_activos.remove(prestamo)
        return f"Devolución registrada: '{prestamo.ejemplar.titulo}' — devuelto por {prestamo.usuario.nombre_completo}."

    def listar_prestamos(self, solo_activos=True):
        lista = [p for p in self._prestamos if p.activo] if solo_activos else self._prestamos
        if not lista: print("  (sin préstamos)"); return
        for p in lista: print(p)

    def _buscar_ejemplar_por_id(self, id_ejemplar):
        return next((e for e in self._ejemplares if e.id_ejemplar == id_ejemplar), None)

    def _buscar_usuario_por_dni(self, dni):
        return next((u for u in self._usuarios if u.dni == dni), None)

    def _buscar_prestamo_activo(self, id_ejemplar):
        return next((p for p in self._prestamos if p.activo and p.ejemplar.id_ejemplar == id_ejemplar), None)
