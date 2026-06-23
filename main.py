"""
main.py — Demostración completa del sistema de biblioteca física.
Trabajo Práctico Final — Programación Avanzada
Licenciatura en Ciencia de Datos, UNAB

Ejecutar con:  python main.py

El script recorre todos los requerimientos técnicos del TP:
  1. Metaclase      ValidarMayuscula
  2. Decorador      @log_operacion
  3. Herencia       Persona → Usuario / Ejemplar → subclases
  4. Polimorfismo   mostrar_detalles()
  5. Agregación     Biblioteca ↔ Ejemplar / Usuario
  6. Composición    Biblioteca → Prestamo
  7. Singleton      una única instancia de Biblioteca
"""

from modelos import EjemplarPrestable, EjemplarConsulta, Usuario
from biblioteca import Biblioteca
from utils import ValidarMayuscula


# ─────────────────────────────────────────────────────────────
# Helpers de presentación
# ─────────────────────────────────────────────────────────────

def seccion(titulo: str):
    ancho = 60
    print("\n" + "═" * ancho)
    print(f"  {titulo}")
    print("═" * ancho)


def subseccion(titulo: str):
    print(f"\n  ── {titulo}")


def intentar(descripcion: str, func, *args, **kwargs):
    """Ejecuta func(*args) y muestra el resultado o el error esperado."""
    print(f"\n  › {descripcion}")
    try:
        func(*args, **kwargs)
    except ValueError as e:
        print(f"    ✔ Rechazado correctamente: {e}")


# ─────────────────────────────────────────────────────────────
# DEMOSTRACIÓN
# ─────────────────────────────────────────────────────────────

def main():

    # ══════════════════════════════════════════════════════════
    # 1. METACLASE — ValidarMayuscula
    # ══════════════════════════════════════════════════════════
    seccion("1 · METACLASE — ValidarMayuscula")

    print("\n  Todas las clases del sistema usan ValidarMayuscula.")
    print("  Si el nombre no empieza con mayúscula → TypeError en definición.\n")

    try:
        class claseInvalida(metaclass=ValidarMayuscula):
            pass
    except TypeError as e:
        print(f"  ✔ TypeError al definir 'claseInvalida': {e}")

    class ClaseValida(metaclass=ValidarMayuscula):
        pass
    print(f"  ✔ 'ClaseValida' creada sin error.")

    # ══════════════════════════════════════════════════════════
    # 2. SINGLETON — una única instancia de Biblioteca
    # ══════════════════════════════════════════════════════════
    seccion("2 · SINGLETON — Biblioteca")

    bib_a = Biblioteca("Biblioteca Central UNAB")
    bib_b = Biblioteca("Intento de segunda instancia")

    print(f"\n  bib_a is bib_b → {bib_a is bib_b}")
    print(f"  Nombre conservado: '{bib_a.nombre}'")
    print(f"  id(bib_a) == id(bib_b): {id(bib_a) == id(bib_b)}")

    bib = bib_a   # referencia de trabajo para el resto del script

    # ══════════════════════════════════════════════════════════
    # 3. HERENCIA + ALTA DE EJEMPLARES  (@log_operacion)
    # ══════════════════════════════════════════════════════════
    seccion("3 · HERENCIA y ALTA DE EJEMPLARES")

    subseccion("Crear ejemplares físicos (mismo ISBN → distintos IDs)")

    # Tres ejemplares prestables del mismo título
    ep1 = EjemplarPrestable(
        "BC-0001", "El Principito", "Antoine de Saint-Exupéry",
        "978-0156013987", dias_prestamo=7
    )
    ep2 = EjemplarPrestable(
        "BC-0002", "El Principito", "Antoine de Saint-Exupéry",
        "978-0156013987", dias_prestamo=7
    )
    ep3 = EjemplarPrestable(
        "BC-0003", "Cien años de soledad", "Gabriel García Márquez",
        "978-0060883287", dias_prestamo=14
    )
    # Ejemplar de solo consulta
    ec1 = EjemplarConsulta(
        "BC-0099", "Enciclopedia Larousse", "Larousse Editorial",
        "978-6072100012", sala="Sala de Referencia"
    )
    ec2 = EjemplarConsulta(
        "BC-0100", "Diccionario de la RAE", "Real Academia Española",
        "978-8467041507", sala="Sala de Referencia"
    )

    print()
    bib.registrar_ejemplar(ep1)
    bib.registrar_ejemplar(ep2)
    bib.registrar_ejemplar(ep3)
    bib.registrar_ejemplar(ec1)
    bib.registrar_ejemplar(ec2)

    subseccion("Intento de ID duplicado")
    intentar(
        "Registrar BC-0001 por segunda vez",
        bib.registrar_ejemplar,
        EjemplarPrestable("BC-0001", "Duplicado", "X", "000")
    )

    # ══════════════════════════════════════════════════════════
    # 4. POLIMORFISMO — mostrar_detalles()
    # ══════════════════════════════════════════════════════════
    seccion("4 · POLIMORFISMO — mostrar_detalles()")

    print("\n  Misma llamada, distintos resultados según el tipo de ejemplar:\n")
    catalogo_mixto = [ep1, ep2, ep3, ec1, ec2]
    for ej in catalogo_mixto:
        print(f"  [{ej.__class__.__name__}]")
        for linea in ej.mostrar_detalles().splitlines():
            print(f"    {linea}")
        print()

    # ══════════════════════════════════════════════════════════
    # 5. ALTA DE USUARIOS (Agregación: Biblioteca ↔ Usuario)
    # ══════════════════════════════════════════════════════════
    seccion("5 · ALTA DE USUARIOS  (Agregación)")

    u1 = Usuario("Ana García",    "30111222", "LIC-001")
    u2 = Usuario("Carlos Ruiz",   "28999000", "LIC-002")
    u3 = Usuario("Lucía Fernández","35444555", "LIC-003")
    print()
    
    bib.registrar_usuario(u1)
    bib.registrar_usuario(u2)
    bib.registrar_usuario(u3)

    subseccion("Intento de legajo duplicado")
    intentar(
        "Registrar LIC-001 por segunda vez",
        bib.registrar_usuario,
        Usuario("Ana Bis", "99999999", "LIC-001")
    )

    subseccion("Usuarios registrados")
    print()
    bib.listar_usuarios()

    # ══════════════════════════════════════════════════════════
    # 6. PRÉSTAMOS  (Composición: Biblioteca crea Prestamo)
    # ══════════════════════════════════════════════════════════
    seccion("6 · PRÉSTAMOS  (Composición)")

    subseccion("Préstamos exitosos")
    print()
    bib.prestar_ejemplar("BC-0001", "LIC-001")   # El Principito → Ana
    bib.prestar_ejemplar("BC-0002", "LIC-002")   # otro ejemplar mismo título → Carlos
    bib.prestar_ejemplar("BC-0003", "LIC-003")   # Cien años → Lucía

    subseccion("Préstamos activos")
    print()
    bib.listar_prestamos(solo_activos=True)

    subseccion("Casos inválidos")
    intentar(
        "Prestar un ejemplar de consulta (BC-0099)",
        bib.prestar_ejemplar, "BC-0099", "LIC-001"
    )
    intentar(
        "Prestar BC-0001 (ya prestado)",
        bib.prestar_ejemplar, "BC-0001", "LIC-003"
    )
    intentar(
        "Prestar BC-0001 a usuario inexistente (LIC-999)",
        bib.prestar_ejemplar, "BC-0001", "LIC-999"
    )

    # ══════════════════════════════════════════════════════════
    # 7. DEVOLUCIONES
    # ══════════════════════════════════════════════════════════
    seccion("7 · DEVOLUCIONES")

    print()
    bib.devolver_ejemplar("BC-0001")
    bib.devolver_ejemplar("BC-0003")

    subseccion("Estado del ejemplar tras devolución")
    print(f"\n  BC-0001 estado: {ep1.estado}")
    print(f"  Préstamos activos de Ana: {len(u1.prestamos_activos)}")

    subseccion("Historial completo de préstamos")
    print()
    bib.listar_prestamos(solo_activos=False)

    intentar(
        "Devolver BC-0001 nuevamente (ya devuelto)",
        bib.devolver_ejemplar, "BC-0001"
    )

    # ══════════════════════════════════════════════════════════
    # 8. BAJAS
    # ══════════════════════════════════════════════════════════
    seccion("8 · BAJAS")

    subseccion("Baja de usuario con préstamo activo")
    intentar(
        "Dar de baja LIC-002 (tiene BC-0002 prestado)",
        bib.dar_baja_usuario, "LIC-002"
    )

    subseccion("Baja de ejemplar prestado")
    intentar(
        "Dar de baja BC-0002 (está prestado)",
        bib.dar_baja_ejemplar, "BC-0002"
    )

    subseccion("Bajas válidas (tras devolución)")
    bib.devolver_ejemplar("BC-0002")
    print()
    bib.dar_baja_ejemplar("BC-0002")
    bib.dar_baja_usuario("LIC-002")

    # ══════════════════════════════════════════════════════════
    # 9. ESTADO FINAL DEL SISTEMA
    # ══════════════════════════════════════════════════════════
    seccion("9 · ESTADO FINAL DEL SISTEMA")

    print()
    print(bib)

    subseccion("Catálogo final")
    print()
    bib.listar_ejemplares()

    subseccion("Usuarios activos")
    print()
    bib.listar_usuarios()

    print("\n" + "═" * 60)
    print("  Demostración completada.")
    print("═" * 60 + "\n")


if __name__ == "__main__":
    main()
