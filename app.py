"""
app.py — Interfaz gráfica del sistema de biblioteca física.
Trabajo Práctico Final — Programación Avanzada
Licenciatura en Ciencia de Datos, UNAB

Ejecutar con:  python app.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
from modelos import EjemplarPrestable, EjemplarConsulta, Usuario
from biblioteca import Biblioteca


# ─────────────────────────────────────────────
# PALETA Y CONSTANTES VISUALES
# ─────────────────────────────────────────────

COLOR_FONDO       = "#F7F7F8"
COLOR_SIDEBAR     = "#1E1E2E"
COLOR_SIDEBAR_SEL = "#313147"
COLOR_ACENTO      = "#7C6AF7"       # violeta
COLOR_ACENTO2     = "#5EC4A8"       # verde menta (préstamos)
COLOR_PELIGRO     = "#E05C5C"       # rojo (bajas / errores)
COLOR_TEXTO       = "#1A1A2E"
COLOR_TEXTO_SUAVE = "#6B6B80"
COLOR_BLANCO      = "#FFFFFF"
COLOR_BORDE       = "#E2E2E8"

FUENTE_TITULO  = ("Segoe UI", 20, "bold")
FUENTE_SECCION = ("Segoe UI", 13, "bold")
FUENTE_NORMAL  = ("Segoe UI", 10)
FUENTE_PEQUEÑA = ("Segoe UI", 9)
FUENTE_BOTON   = ("Segoe UI", 10, "bold")
FUENTE_SIDEBAR = ("Segoe UI", 11)


# ─────────────────────────────────────────────
# VENTANA PRINCIPAL
# ─────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Biblioteca · UNAB")
        self.geometry("1000x640")
        self.minsize(900, 580)
        self.configure(bg=COLOR_FONDO)
        self.resizable(True, True)

        # única instancia del sistema (Singleton)
        self.bib = Biblioteca("Biblioteca Central UNAB")
        self._cargar_datos_demo()

        self._construir_ui()

    # ── datos de ejemplo para no arrancar vacío ──
    def _cargar_datos_demo(self):
        bib = self.bib
        try:
            bib.registrar_ejemplar.__wrapped__(
                bib,
                EjemplarPrestable("BC-0001", "El Principito",
                                  "Antoine de Saint-Exupéry", "978-0156013987", 7)
            )
            bib.registrar_ejemplar.__wrapped__(
                bib,
                EjemplarPrestable("BC-0002", "Cien años de soledad",
                                  "Gabriel García Márquez", "978-0060883287", 14)
            )
            bib.registrar_ejemplar.__wrapped__(
                bib,
                EjemplarConsulta("BC-0099", "Enciclopedia Larousse",
                                 "Larousse Editorial", "978-6072100012", "Sala A")
            )
            bib.registrar_usuario.__wrapped__(
                bib, Usuario("Ana García", "30111222", "LIC-001")
            )
            bib.registrar_usuario.__wrapped__(
                bib, Usuario("Carlos Ruiz", "28999000", "LIC-002")
            )
        except Exception:
            pass   # si ya están cargados (reinicio), ignorar

    # ── estructura: sidebar + área de contenido ──
    def _construir_ui(self):
        # Sidebar
        self.sidebar = tk.Frame(self, bg=COLOR_SIDEBAR, width=210)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Área de contenido
        self.contenido = tk.Frame(self, bg=COLOR_FONDO)
        self.contenido.pack(side="left", fill="both", expand=True)

        self._construir_sidebar()

        # Pantalla activa
        self.pantallas = {}
        for Cls in (PantallaEjemplares, PantallaUsuarios, PantallaPrestamos):
            p = Cls(self.contenido, self.bib, self._refrescar_todo)
            self.pantallas[Cls.CLAVE] = p
            p.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._mostrar("ejemplares")

    def _construir_sidebar(self):
        # Logo / título
        tk.Label(
            self.sidebar, text="📚", font=("Segoe UI", 28),
            bg=COLOR_SIDEBAR, fg=COLOR_ACENTO
        ).pack(pady=(28, 4))
        tk.Label(
            self.sidebar, text="Biblioteca\nUNAB",
            font=("Segoe UI", 12, "bold"), bg=COLOR_SIDEBAR,
            fg=COLOR_BLANCO, justify="center"
        ).pack(pady=(0, 28))

        ttk.Separator(self.sidebar, orient="horizontal").pack(fill="x", padx=16, pady=4)

        # Botones de navegación
        self.botones_nav = {}
        nav = [
            ("ejemplares",  "📖  Ejemplares"),
            ("usuarios",    "👤  Usuarios"),
            ("prestamos",   "🔄  Préstamos"),
        ]
        for clave, etiqueta in nav:
            btn = tk.Button(
                self.sidebar, text=etiqueta,
                font=FUENTE_SIDEBAR, anchor="w", padx=20,
                bg=COLOR_SIDEBAR, fg="#CCCCDD",
                activebackground=COLOR_SIDEBAR_SEL,
                activeforeground=COLOR_BLANCO,
                relief="flat", bd=0, cursor="hand2",
                command=lambda c=clave: self._mostrar(c)
            )
            btn.pack(fill="x", pady=2)
            self.botones_nav[clave] = btn

        # Info singleton al pie
        tk.Frame(self.sidebar, bg=COLOR_SIDEBAR).pack(fill="y", expand=True)
        tk.Label(
            self.sidebar,
            text="🔒 Instancia única\n(Singleton activo)",
            font=("Segoe UI", 8), bg=COLOR_SIDEBAR,
            fg="#555570", justify="center"
        ).pack(pady=16)

    def _mostrar(self, clave: str):
        # Resaltar botón activo
        for k, btn in self.botones_nav.items():
            if k == clave:
                btn.config(bg=COLOR_SIDEBAR_SEL, fg=COLOR_BLANCO)
            else:
                btn.config(bg=COLOR_SIDEBAR, fg="#CCCCDD")

        self.pantallas[clave].tkraise()
        self.pantallas[clave].refrescar()

    def _refrescar_todo(self):
        for p in self.pantallas.values():
            p.refrescar()


# ─────────────────────────────────────────────
# UTILIDADES COMPARTIDAS
# ─────────────────────────────────────────────

def hacer_tabla(parent, columnas: list[tuple], alto: int = 10) -> ttk.Treeview:
    """Crea un Treeview estilizado con scrollbar."""
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Tabla.Treeview",
                    background=COLOR_BLANCO,
                    fieldbackground=COLOR_BLANCO,
                    foreground=COLOR_TEXTO,
                    font=FUENTE_NORMAL,
                    rowheight=30)
    style.configure("Tabla.Treeview.Heading",
                    background=COLOR_FONDO,
                    foreground=COLOR_TEXTO_SUAVE,
                    font=("Segoe UI", 9, "bold"),
                    relief="flat")
    style.map("Tabla.Treeview",
              background=[("selected", COLOR_ACENTO)],
              foreground=[("selected", COLOR_BLANCO)])

    frame = tk.Frame(parent, bg=COLOR_BORDE, bd=1, relief="solid")
    frame.pack(fill="both", expand=True, padx=0, pady=0)

    ids = [c[0] for c in columnas]
    tabla = ttk.Treeview(frame, columns=ids, show="headings",
                         height=alto, style="Tabla.Treeview")

    for col_id, encabezado, ancho in columnas:
        tabla.heading(col_id, text=encabezado)
        tabla.column(col_id, width=ancho, anchor="w", minwidth=60)

    scroll = ttk.Scrollbar(frame, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=scroll.set)

    tabla.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
    return tabla


def campo(parent, etiqueta: str, fila: int, col: int = 0) -> tk.Entry:
    """Label + Entry en grid, devuelve el Entry."""
    tk.Label(parent, text=etiqueta, font=FUENTE_PEQUEÑA,
             bg=COLOR_BLANCO, fg=COLOR_TEXTO_SUAVE,
             anchor="w").grid(row=fila, column=col, sticky="w",
                              padx=(0, 8), pady=(6, 0))
    e = tk.Entry(parent, font=FUENTE_NORMAL, relief="solid", bd=1,
                 bg="#FAFAFA", fg=COLOR_TEXTO, insertbackground=COLOR_ACENTO)
    e.grid(row=fila + 1, column=col, sticky="ew", pady=(2, 0))
    return e


def boton(parent, texto: str, comando, color=COLOR_ACENTO) -> tk.Button:
    """Botón estilizado."""
    return tk.Button(
        parent, text=texto, font=FUENTE_BOTON,
        bg=color, fg=COLOR_BLANCO, activebackground=color,
        activeforeground=COLOR_BLANCO, relief="flat",
        padx=14, pady=7, cursor="hand2", command=comando
    )


def tarjeta(parent, **kwargs) -> tk.Frame:
    """Frame con fondo blanco y borde suave."""
    f = tk.Frame(parent, bg=COLOR_BLANCO, bd=1,
                 relief="solid", **kwargs)
    return f


# ─────────────────────────────────────────────
# PANTALLA BASE
# ─────────────────────────────────────────────

class PantallaBase(tk.Frame):
    CLAVE = ""

    def __init__(self, parent, bib: Biblioteca, refrescar_cb):
        super().__init__(parent, bg=COLOR_FONDO)
        self.bib = bib
        self.refrescar_cb = refrescar_cb
        self._construir()

    def _construir(self):
        raise NotImplementedError

    def refrescar(self):
        pass


# ─────────────────────────────────────────────
# PANTALLA: EJEMPLARES
# ─────────────────────────────────────────────

class PantallaEjemplares(PantallaBase):
    CLAVE = "ejemplares"

    def _construir(self):
        # Encabezado
        cab = tk.Frame(self, bg=COLOR_FONDO)
        cab.pack(fill="x", padx=28, pady=(24, 4))
        tk.Label(cab, text="Ejemplares", font=FUENTE_TITULO,
                 bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(side="left")

        # Contenedor principal: tabla izq, formulario der
        cuerpo = tk.Frame(self, bg=COLOR_FONDO)
        cuerpo.pack(fill="both", expand=True, padx=28, pady=8)
        cuerpo.columnconfigure(0, weight=3)
        cuerpo.columnconfigure(1, weight=2)
        cuerpo.rowconfigure(0, weight=1)

        # ── Tabla ──
        marco_tabla = tk.Frame(cuerpo, bg=COLOR_FONDO)
        marco_tabla.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        self.tabla = hacer_tabla(marco_tabla, [
            ("id",     "ID / Código",  110),
            ("titulo", "Título",        200),
            ("autor",  "Autor",         160),
            ("isbn",   "ISBN",          130),
            ("tipo",   "Tipo",          100),
            ("estado", "Estado",        90),
        ], alto=14)
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)

        # ── Formulario ──
        form = tarjeta(cuerpo)
        form.grid(row=0, column=1, sticky="nsew")

        tk.Label(form, text="Registrar ejemplar", font=FUENTE_SECCION,
                 bg=COLOR_BLANCO, fg=COLOR_TEXTO).pack(anchor="w", padx=20, pady=(18, 4))
        ttk.Separator(form).pack(fill="x", padx=20, pady=4)

        campos_frame = tk.Frame(form, bg=COLOR_BLANCO)
        campos_frame.pack(fill="x", padx=20, pady=4)
        campos_frame.columnconfigure(0, weight=1)

        self.e_id     = campo(campos_frame, "ID / Código de barra", 0)
        self.e_titulo = campo(campos_frame, "Título",               2)
        self.e_autor  = campo(campos_frame, "Autor",                4)
        self.e_isbn   = campo(campos_frame, "ISBN",                 6)

        # Tipo de ejemplar
        tk.Label(campos_frame, text="Tipo de ejemplar", font=FUENTE_PEQUEÑA,
                 bg=COLOR_BLANCO, fg=COLOR_TEXTO_SUAVE,
                 anchor="w").grid(row=8, column=0, sticky="w", pady=(6, 0))
        self.tipo_var = tk.StringVar(value="Prestable")
        marco_tipo = tk.Frame(campos_frame, bg=COLOR_BLANCO)
        marco_tipo.grid(row=9, column=0, sticky="w", pady=(2, 0))
        for val in ("Prestable", "Consulta"):
            tk.Radiobutton(marco_tipo, text=val, variable=self.tipo_var,
                           value=val, font=FUENTE_NORMAL,
                           bg=COLOR_BLANCO, fg=COLOR_TEXTO,
                           activebackground=COLOR_BLANCO,
                           selectcolor=COLOR_BLANCO,
                           command=self._toggle_campos_extra).pack(side="left", padx=(0, 12))

        # Campo extra (días préstamo o sala)
        self.label_extra = tk.Label(campos_frame, text="Días de préstamo",
                                    font=FUENTE_PEQUEÑA, bg=COLOR_BLANCO,
                                    fg=COLOR_TEXTO_SUAVE, anchor="w")
        self.label_extra.grid(row=10, column=0, sticky="w", pady=(6, 0))
        self.e_extra = tk.Entry(campos_frame, font=FUENTE_NORMAL,
                                relief="solid", bd=1, bg="#FAFAFA", fg=COLOR_TEXTO)
        self.e_extra.grid(row=11, column=0, sticky="ew", pady=(2, 0))
        self.e_extra.insert(0, "7")

        # Botones
        btns = tk.Frame(form, bg=COLOR_BLANCO)
        btns.pack(fill="x", padx=20, pady=16)
        boton(btns, "Registrar", self._registrar).pack(fill="x", pady=(0, 6))
        boton(btns, "Dar de baja", self._dar_baja,
              color=COLOR_PELIGRO).pack(fill="x")

        tk.Label(form, text="Seleccioná un ejemplar en la tabla\npara dar de baja.",
                 font=FUENTE_PEQUEÑA, bg=COLOR_BLANCO,
                 fg=COLOR_TEXTO_SUAVE, justify="center").pack(pady=(0, 16))

    def _toggle_campos_extra(self):
        if self.tipo_var.get() == "Prestable":
            self.label_extra.config(text="Días de préstamo")
            self.e_extra.delete(0, "end")
            self.e_extra.insert(0, "7")
        else:
            self.label_extra.config(text="Sala de consulta")
            self.e_extra.delete(0, "end")
            self.e_extra.insert(0, "Sala General")

    def _registrar(self):
        id_ej  = self.e_id.get().strip()
        titulo = self.e_titulo.get().strip()
        autor  = self.e_autor.get().strip()
        isbn   = self.e_isbn.get().strip()
        extra  = self.e_extra.get().strip()

        if not all([id_ej, titulo, autor, isbn, extra]):
            messagebox.showwarning("Campos incompletos",
                                   "Completá todos los campos antes de registrar.")
            return
        try:
            if self.tipo_var.get() == "Prestable":
                ej = EjemplarPrestable(id_ej, titulo, autor, isbn,
                                       dias_prestamo=int(extra))
            else:
                ej = EjemplarConsulta(id_ej, titulo, autor, isbn, sala=extra)
            self.bib.registrar_ejemplar(ej)
            messagebox.showinfo("✔ Registrado",
                                f"Ejemplar '{id_ej}' registrado correctamente.")
            self._limpiar()
            self.refrescar_cb()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _dar_baja(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Sin selección",
                                   "Seleccioná un ejemplar en la tabla.")
            return
        id_ej = self.tabla.item(sel[0])["values"][0]
        confirmar = messagebox.askyesno(
            "Confirmar baja",
            f"¿Dar de baja el ejemplar '{id_ej}'?"
        )
        if confirmar:
            try:
                self.bib.dar_baja_ejemplar(str(id_ej))
                messagebox.showinfo("✔ Baja", f"Ejemplar '{id_ej}' dado de baja.")
                self.refrescar_cb()
            except ValueError as e:
                messagebox.showerror("No se puede dar de baja", str(e))

    def _al_seleccionar(self, event):
        pass  # reservado para extensiones futuras

    def _limpiar(self):
        for e in (self.e_id, self.e_titulo, self.e_autor, self.e_isbn):
            e.delete(0, "end")
        self.e_extra.delete(0, "end")
        self.e_extra.insert(0, "7")

    def refrescar(self):
        self.tabla.delete(*self.tabla.get_children())
        for ej in self.bib._ejemplares:
            tipo   = "Prestable" if isinstance(ej, EjemplarPrestable) else "Consulta"
            estado = ej.estado if isinstance(ej, EjemplarPrestable) else ej.sala
            self.tabla.insert("", "end", values=(
                ej.id_ejemplar, ej.titulo, ej.autor, ej.isbn, tipo, estado
            ))


# ─────────────────────────────────────────────
# PANTALLA: USUARIOS
# ─────────────────────────────────────────────

class PantallaUsuarios(PantallaBase):
    CLAVE = "usuarios"

    def _construir(self):
        cab = tk.Frame(self, bg=COLOR_FONDO)
        cab.pack(fill="x", padx=28, pady=(24, 4))
        tk.Label(cab, text="Usuarios", font=FUENTE_TITULO,
                 bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(side="left")

        cuerpo = tk.Frame(self, bg=COLOR_FONDO)
        cuerpo.pack(fill="both", expand=True, padx=28, pady=8)
        cuerpo.columnconfigure(0, weight=3)
        cuerpo.columnconfigure(1, weight=2)
        cuerpo.rowconfigure(0, weight=1)

        # ── Tabla ──
        marco_tabla = tk.Frame(cuerpo, bg=COLOR_FONDO)
        marco_tabla.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        self.tabla = hacer_tabla(marco_tabla, [
            ("legajo",   "Legajo",            110),
            ("nombre",   "Nombre",            200),
            ("dni",      "DNI",               110),
            ("prestamos","Préstamos activos", 130),
        ], alto=14)

        # ── Formulario ──
        form = tarjeta(cuerpo)
        form.grid(row=0, column=1, sticky="nsew")

        tk.Label(form, text="Registrar usuario", font=FUENTE_SECCION,
                 bg=COLOR_BLANCO, fg=COLOR_TEXTO).pack(anchor="w", padx=20, pady=(18, 4))
        ttk.Separator(form).pack(fill="x", padx=20, pady=4)

        campos_frame = tk.Frame(form, bg=COLOR_BLANCO)
        campos_frame.pack(fill="x", padx=20, pady=4)
        campos_frame.columnconfigure(0, weight=1)

        self.e_nombre = campo(campos_frame, "Nombre completo", 0)
        self.e_dni    = campo(campos_frame, "DNI",             2)
        self.e_legajo = campo(campos_frame, "Legajo",          4)

        btns = tk.Frame(form, bg=COLOR_BLANCO)
        btns.pack(fill="x", padx=20, pady=16)
        boton(btns, "Registrar", self._registrar).pack(fill="x", pady=(0, 6))
        boton(btns, "Dar de baja", self._dar_baja,
              color=COLOR_PELIGRO).pack(fill="x")

        tk.Label(form, text="Seleccioná un usuario en la tabla\npara dar de baja.",
                 font=FUENTE_PEQUEÑA, bg=COLOR_BLANCO,
                 fg=COLOR_TEXTO_SUAVE, justify="center").pack(pady=(0, 16))

    def _registrar(self):
        nombre = self.e_nombre.get().strip()
        dni    = self.e_dni.get().strip()
        legajo = self.e_legajo.get().strip()

        if not all([nombre, dni, legajo]):
            messagebox.showwarning("Campos incompletos",
                                   "Completá todos los campos.")
            return
        try:
            self.bib.registrar_usuario(Usuario(nombre, dni, legajo))
            messagebox.showinfo("✔ Registrado",
                                f"Usuario '{nombre}' registrado correctamente.")
            for e in (self.e_nombre, self.e_dni, self.e_legajo):
                e.delete(0, "end")
            self.refrescar_cb()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _dar_baja(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Sin selección",
                                   "Seleccioná un usuario en la tabla.")
            return
        legajo = self.tabla.item(sel[0])["values"][0]
        confirmar = messagebox.askyesno(
            "Confirmar baja",
            f"¿Dar de baja al usuario con legajo '{legajo}'?"
        )
        if confirmar:
            try:
                self.bib.dar_baja_usuario(str(legajo))
                messagebox.showinfo("✔ Baja", "Usuario dado de baja.")
                self.refrescar_cb()
            except ValueError as e:
                messagebox.showerror("No se puede dar de baja", str(e))

    def refrescar(self):
        self.tabla.delete(*self.tabla.get_children())
        for u in self.bib._usuarios:
            self.tabla.insert("", "end", values=(
                u.legajo, u.nombre, u.dni, len(u.prestamos_activos)
            ))


# ─────────────────────────────────────────────
# PANTALLA: PRÉSTAMOS
# ─────────────────────────────────────────────

class PantallaPrestamos(PantallaBase):
    CLAVE = "prestamos"

    def _construir(self):
        cab = tk.Frame(self, bg=COLOR_FONDO)
        cab.pack(fill="x", padx=28, pady=(24, 4))
        tk.Label(cab, text="Préstamos", font=FUENTE_TITULO,
                 bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(side="left")

        cuerpo = tk.Frame(self, bg=COLOR_FONDO)
        cuerpo.pack(fill="both", expand=True, padx=28, pady=8)
        cuerpo.columnconfigure(0, weight=3)
        cuerpo.columnconfigure(1, weight=2)
        cuerpo.rowconfigure(0, weight=1)

        # ── Tabla ──
        marco_tabla = tk.Frame(cuerpo, bg=COLOR_FONDO)
        marco_tabla.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        self.tabla = hacer_tabla(marco_tabla, [
            ("id_ej",    "ID Ejemplar",  110),
            ("titulo",   "Título",       180),
            ("usuario",  "Usuario",      140),
            ("inicio",   "Desde",         90),
            ("limite",   "Límite",        90),
            ("estado",   "Estado",        90),
        ], alto=14)

        # ── Panel de acciones ──
        panel = tarjeta(cuerpo)
        panel.grid(row=0, column=1, sticky="nsew")

        # Nuevo préstamo
        tk.Label(panel, text="Nuevo préstamo", font=FUENTE_SECCION,
                 bg=COLOR_BLANCO, fg=COLOR_TEXTO).pack(anchor="w", padx=20, pady=(18, 4))
        ttk.Separator(panel).pack(fill="x", padx=20, pady=4)

        campos_frame = tk.Frame(panel, bg=COLOR_BLANCO)
        campos_frame.pack(fill="x", padx=20, pady=4)
        campos_frame.columnconfigure(0, weight=1)

        self.e_id_ej  = campo(campos_frame, "ID del ejemplar",  0)
        self.e_legajo = campo(campos_frame, "Legajo del usuario", 2)

        boton(campos_frame, "Registrar préstamo",
              self._prestar, color=COLOR_ACENTO2
              ).grid(row=4, column=0, sticky="ew", pady=(14, 0))

        # Devolución
        ttk.Separator(panel).pack(fill="x", padx=20, pady=16)
        tk.Label(panel, text="Devolución", font=FUENTE_SECCION,
                 bg=COLOR_BLANCO, fg=COLOR_TEXTO).pack(anchor="w", padx=20, pady=(0, 4))

        dev_frame = tk.Frame(panel, bg=COLOR_BLANCO)
        dev_frame.pack(fill="x", padx=20)
        dev_frame.columnconfigure(0, weight=1)

        self.e_id_dev = campo(dev_frame, "ID del ejemplar a devolver", 0)
        boton(dev_frame, "Registrar devolución",
              self._devolver, color=COLOR_PELIGRO
              ).grid(row=2, column=0, sticky="ew", pady=(14, 0))

        tk.Label(panel, text="O seleccioná un préstamo activo\nen la tabla para autocompletar.",
                 font=FUENTE_PEQUEÑA, bg=COLOR_BLANCO,
                 fg=COLOR_TEXTO_SUAVE, justify="center").pack(pady=12)

        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)

    def _al_seleccionar(self, event):
        sel = self.tabla.selection()
        if sel:
            id_ej = self.tabla.item(sel[0])["values"][0]
            self.e_id_dev.delete(0, "end")
            self.e_id_dev.insert(0, str(id_ej))

    def _prestar(self):
        id_ej  = self.e_id_ej.get().strip()
        legajo = self.e_legajo.get().strip()
        if not all([id_ej, legajo]):
            messagebox.showwarning("Campos incompletos",
                                   "Completá el ID del ejemplar y el legajo.")
            return
        try:
            self.bib.prestar_ejemplar(id_ej, legajo)
            messagebox.showinfo("✔ Préstamo registrado",
                                f"Ejemplar '{id_ej}' prestado correctamente.")
            self.e_id_ej.delete(0, "end")
            self.e_legajo.delete(0, "end")
            self.refrescar_cb()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _devolver(self):
        id_ej = self.e_id_dev.get().strip()
        if not id_ej:
            messagebox.showwarning("Campo vacío",
                                   "Ingresá el ID del ejemplar a devolver.")
            return
        try:
            self.bib.devolver_ejemplar(id_ej)
            messagebox.showinfo("✔ Devolución registrada",
                                f"Ejemplar '{id_ej}' devuelto correctamente.")
            self.e_id_dev.delete(0, "end")
            self.refrescar_cb()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def refrescar(self):
        self.tabla.delete(*self.tabla.get_children())
        for p in self.bib._prestamos:
            estado = "Activo" if p.activo else f"Devuelto"
            if p.vencido:
                estado = "⚠ Vencido"
            self.tabla.insert("", "end", values=(
                p.ejemplar.id_ejemplar,
                p.ejemplar.titulo,
                p.usuario.nombre,
                str(p.fecha_inicio),
                str(p.fecha_limite),
                estado,
            ))


# ─────────────────────────────────────────────
# PUNTO DE ENTRADA
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app = App()
    app.mainloop()
