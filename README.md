# TP Final — Sistema de Biblioteca Física
**Programación Avanzada · Licenciatura en Ciencia de Datos · UNAB**

## Cómo ejecutar

```bash
python main.py
```

No requiere dependencias externas. Solo Python 3.10+.

## Estructura del proyecto

```
tp_biblioteca/
├── utils.py        # Metaclase ValidarMayuscula + decorador @log_operacion
├── modelos.py      # Persona, Usuario, Ejemplar, EjemplarPrestable, EjemplarConsulta
├── biblioteca.py   # Prestamo + Biblioteca (Singleton)
└── main.py         # Demostración completa de todos los requerimientos
```

## Requerimientos técnicos implementados

| Requerimiento     | Archivo        | Detalle |
|-------------------|----------------|---------|
| Herencia          | `modelos.py`   | `Usuario(Persona)`, `EjemplarPrestable(Ejemplar)`, `EjemplarConsulta(Ejemplar)` |
| Polimorfismo      | `modelos.py`   | `mostrar_detalles()` sobreescrito en cada subclase |
| Agregación        | `biblioteca.py`| `Biblioteca` recibe `Ejemplar` y `Usuario` externos |
| Composición       | `biblioteca.py`| `Biblioteca` crea y destruye objetos `Prestamo` |
| Decorador propio  | `utils.py`     | `@log_operacion` registra alta/baja/préstamo en consola |
| Metaclase         | `utils.py`     | `ValidarMayuscula(type)` valida nombres de clase |
| Singleton         | `biblioteca.py`| Una única instancia de `Biblioteca` en todo el sistema |
