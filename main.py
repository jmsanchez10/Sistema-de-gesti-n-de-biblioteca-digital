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
  8. Validaciones   ISBN, año, email, DNI, páginas
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
    print(f"\n  › {descripcion}")
    try:
        func(*args, **kwargs)
    except (ValueError, TypeError) as e:
        print(f"    ✔ Rechazado correctamente: {e}")


# ─────────────────────────────────────────────────────────────
# DEMOSTRACIÓN
# ─────────────────────────────────────────────────────────────

def main():

    # ══════════════════════════════════════════════════════════
    # 1. METACLASE — ValidarMayuscula
    # ══════════════════════════════════════════════════════════
    seccion("1 · METACLASE — ValidarMayuscula")
    print("\n  Valida que los nombres de clase comiencen con mayúscula.")
    print("  La validación ocurre en tiempo de definición, no de ejecución.\n")

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

    print(f"\n  bib_a is bib_b  →  {bib_a is bib_b}")
    print(f"  Nombre conservado: '{bib_a.nombre}'")
    print(f"  id(bib_a) == id(bib_b): {id(bib_a) == id(bib_b)}")

    bib = bib_a

    # ══════════════════════════════════════════════════════════
    # 3. VALIDACIONES
    # ══════════════════════════════════════════════════════════
    seccion("3 · VALIDACIONES de datos de entrada")

    subseccion("ISBN inválido")
    intentar("ISBN con formato incorrecto",
             EjemplarPrestable, "X", "Título", "Autor", "123-INVALIDO", 2000, 100)

    subseccion("Año de publicación inválido")
    intentar("Año futuro (9999)",
             EjemplarPrestable, "X", "Título", "Autor", "9780156013987", 9999, 100)

    subseccion("Email inválido")
    intentar("Email sin @",
             Usuario, "Juan", "Pérez", "30000001", "correo-sin-arroba")

    subseccion("DNI inválido")
    intentar("DNI con letras",
             Usuario, "Juan", "Pérez", "ABCDEFG", "juan@mail.com")

    subseccion("Páginas inválidas")
    intentar("Páginas = 0",
             EjemplarPrestable, "X", "Título", "Autor", "9780156013987", 2000, 0)

    # ══════════════════════════════════════════════════════════
    # 4. HERENCIA + ALTA DE EJEMPLARES  (@log_operacion)
    # ══════════════════════════════════════════════════════════
    seccion("4 · HERENCIA y ALTA DE EJEMPLARES  (@log_operacion)")

    subseccion("Crear ejemplares físicos (mismo ISBN → distintos IDs)")
    print()

    ep1 = EjemplarPrestable(
        "BC-0001", "El Principito", "Antoine de Saint-Exupéry",
        "9780156013987", 1943, 96, dias_prestamo=7)
    ep2 = EjemplarPrestable(
        "BC-0002", "El Principito", "Antoine de Saint-Exupéry",
        "9780156013987", 1943, 96, dias_prestamo=7)
    ep3 = EjemplarPrestable(
        "BC-0003", "Cien años de soledad", "Gabriel García Márquez",
        "9780060883287", 1967, 432, dias_prestamo=14)
    ec1 = EjemplarConsulta(
        "BC-0099", "Enciclopedia Larousse", "Larousse Editorial",
        "9786072100012", 2020, 1200, sala="Sala de Referencia")
    ec2 = EjemplarConsulta(
        "BC-0100", "Diccionario de la RAE", "Real Academia Española",
        "9788467041507", 2014, 2200, sala="Sala de Referencia")

    bib.registrar_ejemplar(ep1)
    bib.registrar_ejemplar(ep2)
    bib.registrar_ejemplar(ep3)
    bib.registrar_ejemplar(ec1)
    bib.registrar_ejemplar(ec2)

    subseccion("ID duplicado rechazado")
    intentar("Registrar BC-0001 por segunda vez",
             bib.registrar_ejemplar,
             EjemplarPrestable("BC-0001", "Duplicado", "X", "9780156013987", 2000, 100))

    # ══════════════════════════════════════════════════════════
    # 5. POLIMORFISMO — mostrar_detalles()
    # ══════════════════════════════════════════════════════════
    seccion("5 · POLIMORFISMO — mostrar_detalles()")

    print("\n  Misma llamada, distintos resultados según el tipo de ejemplar:\n")
    for ej in [ep1, ep3, ec1]:
        print(f"  [{ej.__class__.__name__}]")
        for linea in ej.mostrar_detalles().splitlines():
            print(f"    {linea}")
        print()

    # ══════════════════════════════════════════════════════════
    # 6. ALTA DE USUARIOS  (Agregación)
    # ══════════════════════════════════════════════════════════
    seccion("6 · ALTA DE USUARIOS  (Agregación)")

    u1 = Usuario("Ana",   "García", "30111222", "ana@mail.com")
    u2 = Usuario("Carlos","Ruiz",   "28999000", "carlos@mail.com")
    u3 = Usuario("Lucía", "Fernández", "35444555", "lucia@mail.com")

    print()
    bib.registrar_usuario(u1)
    bib.registrar_usuario(u2)
    bib.registrar_usuario(u3)

    subseccion("DNI duplicado rechazado")
    intentar("Registrar DNI 30111222 por segunda vez",
             bib.registrar_usuario,
             Usuario("Ana Bis", "Bis", "30111222", "anabis@mail.com"))

    subseccion("Usuarios registrados")
    print()
    bib.listar_usuarios()

    # ══════════════════════════════════════════════════════════
    # 7. PRÉSTAMOS  (Composición)
    # ══════════════════════════════════════════════════════════
    seccion("7 · PRÉSTAMOS  (Composición)")

    subseccion("Préstamos exitosos")
    print()
    bib.prestar_ejemplar("BC-0001", "30111222")
    bib.prestar_ejemplar("BC-0002", "28999000")
    bib.prestar_ejemplar("BC-0003", "35444555")

    subseccion("Préstamos activos")
    print()
    bib.listar_prestamos(solo_activos=True)

    subseccion("Casos inválidos")
    intentar("Prestar ejemplar de consulta (BC-0099)",
             bib.prestar_ejemplar, "BC-0099", "30111222")
    intentar("Prestar BC-0001 (ya prestado)",
             bib.prestar_ejemplar, "BC-0001", "35444555")
    intentar("Prestar a usuario inexistente (DNI 00000000)",
             bib.prestar_ejemplar, "BC-0001", "00000000")

    # ══════════════════════════════════════════════════════════
    # 8. DEVOLUCIONES
    # ══════════════════════════════════════════════════════════
    seccion("8 · DEVOLUCIONES")

    print()
    bib.devolver_ejemplar("BC-0001")
    bib.devolver_ejemplar("BC-0003")

    subseccion("Estado tras devolución")
    print(f"\n  BC-0001 estado : {ep1.estado}")
    print(f"  Préstamos activos de Ana: {len(u1.prestamos_activos)}")

    subseccion("Historial completo de préstamos")
    print()
    bib.listar_prestamos(solo_activos=False)

    intentar("Devolver BC-0001 nuevamente (ya devuelto)",
             bib.devolver_ejemplar, "BC-0001")

    # ══════════════════════════════════════════════════════════
    # 9. MODIFICACIONES
    # ══════════════════════════════════════════════════════════
    seccion("9 · MODIFICACIONES")

    print()
    bib.modificar_ejemplar("BC-0002", titulo="El Principito (Ed. Especial)", dias_prestamo=10)
    bib.modificar_usuario("28999000", email="carlos.nuevo@mail.com")

    subseccion("Verificar cambios")
    print(f"\n  Nuevo título BC-0002 : {ep2.titulo}")
    print(f"  Nuevo email Carlos  : {u2.email}")

    # ══════════════════════════════════════════════════════════
    # 10. BAJAS
    # ══════════════════════════════════════════════════════════
    seccion("10 · BAJAS")

    subseccion("Baja de usuario con préstamo activo")
    intentar("Dar de baja Carlos (tiene BC-0002 prestado)",
             bib.dar_baja_usuario, "28999000")

    subseccion("Baja de ejemplar prestado")
    intentar("Dar de baja BC-0002 (está prestado)",
             bib.dar_baja_ejemplar, "BC-0002")

    subseccion("Bajas válidas tras devolución")
    bib.devolver_ejemplar("BC-0002")
    print()
    bib.dar_baja_ejemplar("BC-0002")
    bib.dar_baja_usuario("28999000")

    # ══════════════════════════════════════════════════════════
    # 11. ESTADO FINAL
    # ══════════════════════════════════════════════════════════
    seccion("11 · ESTADO FINAL DEL SISTEMA")

    print()
    print(bib)

    subseccion("Catálogo final")
    print()
    bib.listar_ejemplares()

    subseccion("Usuarios activos")
    print()
    bib.listar_usuarios()

    print("\n" + "═" * 60)
    print("  Demostración completada exitosamente.")
    print("═" * 60 + "\n")


if __name__ == "__main__":
    main()
