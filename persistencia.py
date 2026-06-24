"""
persistencia.py — Guardado y carga de datos en formato JSON.
"""
import json
from pathlib import Path
from datetime import date
from modelos import EjemplarPrestable, EjemplarConsulta, Usuario
from biblioteca import Prestamo

RUTA_DATOS = Path(__file__).parent / "datos.json"

def _ejemplar_a_dict(ej) -> dict:
    base = {
        "tipo": "prestable" if isinstance(ej, EjemplarPrestable) else "consulta",
        "id_ejemplar": ej.id_ejemplar, "titulo": ej.titulo, "autor": ej.autor,
        "isbn": ej.isbn, "anio_publicacion": ej.anio_publicacion, "cantidad_paginas": ej.cantidad_paginas,
    }
    if isinstance(ej, EjemplarPrestable):
        base["estado"] = ej.estado; base["dias_prestamo"] = ej.dias_prestamo
    else:
        base["sala"] = ej.sala
    return base

def _usuario_a_dict(u) -> dict:
    return {"nombre": u.nombre, "apellido": u.apellido, "dni": u.dni, "email": u.email}

def _prestamo_a_dict(p) -> dict:
    return {
        "id_ejemplar": p.ejemplar.id_ejemplar, "dni_usuario": p.usuario.dni,
        "fecha_inicio": str(p.fecha_inicio), "fecha_limite": str(p.fecha_limite),
        "fecha_devol": str(p.fecha_devol) if p.fecha_devol else None,
    }

def _dict_a_ejemplar(d: dict):
    if d["tipo"] == "prestable":
        ej = EjemplarPrestable(d["id_ejemplar"], d["titulo"], d["autor"], d["isbn"],
                               d["anio_publicacion"], d["cantidad_paginas"], d["dias_prestamo"])
        ej.estado = d["estado"]
        return ej
    return EjemplarConsulta(d["id_ejemplar"], d["titulo"], d["autor"], d["isbn"],
                            d["anio_publicacion"], d["cantidad_paginas"], d["sala"])

def _dict_a_usuario(d: dict) -> Usuario:
    return Usuario(d["nombre"], d["apellido"], d["dni"], d["email"])

def _dict_a_prestamo(d: dict, ejemplares: list, usuarios: list):
    ej = next((e for e in ejemplares if e.id_ejemplar == d["id_ejemplar"]), None)
    u  = next((u for u in usuarios   if u.dni         == d["dni_usuario"]),  None)
    if not ej or not u: return None
    p = Prestamo.__new__(Prestamo)
    p.ejemplar     = ej
    p.usuario      = u
    p.fecha_inicio = date.fromisoformat(d["fecha_inicio"])
    p.fecha_limite = date.fromisoformat(d["fecha_limite"])
    p.fecha_devol  = date.fromisoformat(d["fecha_devol"]) if d["fecha_devol"] else None
    if p.activo:
        u.prestamos_activos.append(p)
    return p

def guardar_datos(biblioteca) -> None:
    datos = {
        "ejemplares": [_ejemplar_a_dict(e) for e in biblioteca._ejemplares],
        "usuarios":   [_usuario_a_dict(u)  for u in biblioteca._usuarios],
        "prestamos":  [_prestamo_a_dict(p) for p in biblioteca._prestamos],
    }
    with open(RUTA_DATOS, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

def cargar_datos(biblioteca) -> bool:
    if not RUTA_DATOS.exists(): return False
    with open(RUTA_DATOS, encoding="utf-8") as f:
        datos = json.load(f)
    for d in datos.get("ejemplares", []):
        biblioteca._ejemplares.append(_dict_a_ejemplar(d))
    for d in datos.get("usuarios", []):
        biblioteca._usuarios.append(_dict_a_usuario(d))
    for d in datos.get("prestamos", []):
        p = _dict_a_prestamo(d, biblioteca._ejemplares, biblioteca._usuarios)
        if p: biblioteca._prestamos.append(p)
    return True
