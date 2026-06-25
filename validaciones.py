"""
validaciones.py — Funciones de validación de datos de entrada.

Usadas por Ejemplar y Usuario antes de asignar atributos,
y por la interfaz gráfica para dar feedback inmediato al usuario.
"""
import re
from datetime import date


def validar_isbn(isbn: str) -> str:
    """
    Acepta ISBN-10 (9 dígitos + dígito/X) e ISBN-13 (13 dígitos).
    Elimina guiones y espacios antes de validar.
    """
    limpio = isbn.replace("-", "").replace(" ", "")
    if len(limpio) == 10:
        if not re.fullmatch(r"\d{9}[\dX]", limpio):
            raise ValueError(f"ISBN inválido: '{isbn}'. Debe tener 10 caracteres (ISBN-10).")
    elif len(limpio) == 13:
        if not re.fullmatch(r"\d{13}", limpio):
            raise ValueError(f"ISBN inválido: '{isbn}'. Debe tener 13 dígitos (ISBN-13).")
    else:
        raise ValueError(
            f"ISBN inválido: '{isbn}'. Debe tener 10 (ISBN-10) o 13 (ISBN-13) caracteres.")
    return limpio


def validar_anio(anio: int) -> int:
    anio_actual = date.today().year
    if not (1000 <= anio <= anio_actual):
        raise ValueError(
            f"Año de publicación inválido: {anio}. "
            f"Debe estar entre 1000 y {anio_actual}.")
    return anio


def validar_paginas(paginas: int) -> int:
    if paginas < 1:
        raise ValueError(f"Cantidad de páginas inválida: {paginas}. Debe ser mayor a 0.")
    if paginas > 99999:
        raise ValueError(f"Cantidad de páginas inválida: {paginas}. Valor demasiado alto.")
    return paginas


def validar_email(email: str) -> str:
    patron = r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$"
    if not re.fullmatch(patron, email):
        raise ValueError(f"Email inválido: '{email}'. Formato esperado: usuario@dominio.com")
    return email.lower()


def validar_dni(dni: str) -> str:
    limpio = dni.replace(".", "").replace(" ", "")
    if not re.fullmatch(r"\d{7,8}", limpio):
        raise ValueError(
            f"DNI inválido: '{dni}'. Debe contener 7 u 8 dígitos numéricos.")
    return limpio


def validar_dias_prestamo(dias: int) -> int:
    if not (1 <= dias <= 365):
        raise ValueError(
            f"Días de préstamo inválidos: {dias}. Debe estar entre 1 y 365.")
    return dias
