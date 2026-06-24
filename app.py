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
from persistencia import guardar_datos, cargar_datos

COLOR_FONDO       = "#F7F7F8"
COLOR_SIDEBAR     = "#1E1E2E"
COLOR_SIDEBAR_SEL = "#313147"
COLOR_ACENTO      = "#7C6AF7"
COLOR_ACENTO2     = "#5EC4A8"
COLOR_PELIGRO     = "#E05C5C"
COLOR_NARANJA     = "#F0A500"
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


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Biblioteca · UNAB")
        self.geometry("1060x680")
        self.minsize(960, 600)
        self.configure(bg=COLOR_FONDO)

        self.bib = Biblioteca("Biblioteca Central UNAB")

        hay_datos = cargar_datos(self.bib)
        if not hay_datos:
            self._cargar_datos_demo()

        self._construir_ui()
        self.protocol("WM_DELETE_WINDOW", self._al_cerrar)

    def _al_cerrar(self):
        guardar_datos(self.bib)
        self.destroy()

    def _cargar_datos_demo(self):
        bib = self.bib
        try:
            bib.registrar_ejemplar.__wrapped__(bib, EjemplarPrestable(
                "BC-0001", "El Principito", "Antoine de Saint-Exupéry", "978-0156013987", 1943, 96, 7))
            bib.registrar_ejemplar.__wrapped__(bib, EjemplarPrestable(
                "BC-0002", "Cien años de soledad", "Gabriel García Márquez", "978-0060883287", 1967, 432, 14))
            bib.registrar_ejemplar.__wrapped__(bib, EjemplarConsulta(
                "BC-0099", "Enciclopedia Larousse", "Larousse Editorial", "978-6072100012", 2020, 1200, "Sala A"))
            bib.registrar_usuario.__wrapped__(bib, Usuario("Ana", "García", "30111222", "ana@mail.com"))
            bib.registrar_usuario.__wrapped__(bib, Usuario("Carlos", "Ruiz", "28999000", "carlos@mail.com"))
        except Exception:
            pass

    def _construir_ui(self):
        self.sidebar = tk.Frame(self, bg=COLOR_SIDEBAR, width=210)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self.contenido = tk.Frame(self, bg=COLOR_FONDO)
        self.contenido.pack(side="left", fill="both", expand=True)
        self._construir_sidebar()
        self.pantallas = {}
        for Cls in (PantallaDashboard, PantallaEjemplares, PantallaUsuarios, PantallaPrestamos):
            p = Cls(self.contenido, self.bib, self._refrescar_todo)
            self.pantallas[Cls.CLAVE] = p
            p.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._mostrar("dashboard")

    def _construir_sidebar(self):
        tk.Label(self.sidebar, text="📚", font=("Segoe UI", 28),
                 bg=COLOR_SIDEBAR, fg=COLOR_ACENTO).pack(pady=(28, 4))
        tk.Label(self.sidebar, text="Biblioteca\nUNAB",
                 font=("Segoe UI", 12, "bold"), bg=COLOR_SIDEBAR,
                 fg=COLOR_BLANCO, justify="center").pack(pady=(0, 28))
        ttk.Separator(self.sidebar).pack(fill="x", padx=16, pady=4)
        self.botones_nav = {}
        for clave, etiqueta in [
            ("dashboard",  "🏠  Inicio"),
            ("ejemplares", "📖  Ejemplares"),
            ("usuarios",   "👤  Usuarios"),
            ("prestamos",  "🔄  Préstamos"),
        ]:
            btn = tk.Button(self.sidebar, text=etiqueta, font=FUENTE_SIDEBAR,
                            anchor="w", padx=20, bg=COLOR_SIDEBAR, fg="#CCCCDD",
                            activebackground=COLOR_SIDEBAR_SEL, activeforeground=COLOR_BLANCO,
                            relief="flat", bd=0, cursor="hand2",
                            command=lambda c=clave: self._mostrar(c))
            btn.pack(fill="x", pady=2)
            self.botones_nav[clave] = btn
        tk.Frame(self.sidebar, bg=COLOR_SIDEBAR).pack(fill="y", expand=True)
        tk.Label(self.sidebar, text="🔒 Instancia única\n(Singleton activo)",
                 font=("Segoe UI", 8), bg=COLOR_SIDEBAR, fg="#555570",
                 justify="center").pack(pady=16)

    def _mostrar(self, clave: str):
        for k, btn in self.botones_nav.items():
            btn.config(bg=COLOR_SIDEBAR_SEL if k == clave else COLOR_SIDEBAR,
                       fg=COLOR_BLANCO if k == clave else "#CCCCDD")
        self.pantallas[clave].tkraise()
        self.pantallas[clave].refrescar()

    def _refrescar_todo(self):
        for p in self.pantallas.values():
            p.refrescar()


def hacer_tabla(parent, columnas, alto=10):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Tabla.Treeview", background=COLOR_BLANCO, fieldbackground=COLOR_BLANCO,
                    foreground=COLOR_TEXTO, font=FUENTE_NORMAL, rowheight=28)
    style.configure("Tabla.Treeview.Heading", background=COLOR_FONDO,
                    foreground=COLOR_TEXTO_SUAVE, font=("Segoe UI", 9, "bold"), relief="flat")
    style.map("Tabla.Treeview",
              background=[("selected", COLOR_ACENTO)], foreground=[("selected", COLOR_BLANCO)])
    frame = tk.Frame(parent, bg=COLOR_BORDE, bd=1, relief="solid")
    frame.pack(fill="both", expand=True)
    ids = [c[0] for c in columnas]
    tabla = ttk.Treeview(frame, columns=ids, show="headings", height=alto, style="Tabla.Treeview")
    for col_id, encabezado, ancho in columnas:
        tabla.heading(col_id, text=encabezado)
        tabla.column(col_id, width=ancho, anchor="w", minwidth=50)
    scroll = ttk.Scrollbar(frame, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=scroll.set)
    tabla.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
    return tabla

def campo(parent, etiqueta, fila, col=0):
    tk.Label(parent, text=etiqueta, font=FUENTE_PEQUEÑA, bg=COLOR_BLANCO,
             fg=COLOR_TEXTO_SUAVE, anchor="w").grid(row=fila, column=col, sticky="w", pady=(6, 0))
    e = tk.Entry(parent, font=FUENTE_NORMAL, relief="solid", bd=1,
                 bg="#FAFAFA", fg=COLOR_TEXTO, insertbackground=COLOR_ACENTO)
    e.grid(row=fila + 1, column=col, sticky="ew", pady=(2, 0))
    return e

def boton(parent, texto, comando, color=COLOR_ACENTO):
    return tk.Button(parent, text=texto, font=FUENTE_BOTON, bg=color, fg=COLOR_BLANCO,
                     activebackground=color, activeforeground=COLOR_BLANCO,
                     relief="flat", padx=14, pady=7, cursor="hand2", command=comando)

def tarjeta(parent, **kw):
    return tk.Frame(parent, bg=COLOR_BLANCO, bd=1, relief="solid", **kw)


class PantallaBase(tk.Frame):
    CLAVE = ""
    def __init__(self, parent, bib, refrescar_cb):
        super().__init__(parent, bg=COLOR_FONDO)
        self.bib = bib
        self.refrescar_cb = refrescar_cb
        self._construir()
    def _construir(self): raise NotImplementedError
    def refrescar(self): pass


# ── DASHBOARD ──────────────────────────────────────────────────────

class PantallaDashboard(PantallaBase):
    CLAVE = "dashboard"

    def _construir(self):
        tk.Label(self, text="Bienvenido al Sistema de Biblioteca",
                 font=FUENTE_TITULO, bg=COLOR_FONDO, fg=COLOR_TEXTO
                 ).pack(anchor="w", padx=32, pady=(28, 4))
        tk.Label(self, text="Biblioteca Central UNAB  —  resumen del sistema",
                 font=FUENTE_NORMAL, bg=COLOR_FONDO, fg=COLOR_TEXTO_SUAVE
                 ).pack(anchor="w", padx=32, pady=(0, 24))

        # Fila de tarjetas de estadísticas
        fila = tk.Frame(self, bg=COLOR_FONDO)
        fila.pack(fill="x", padx=32)

        self.cards = {}
        definiciones = [
            ("ejemplares",  "📖", "Ejemplares",         COLOR_ACENTO),
            ("usuarios",    "👤", "Usuarios",            COLOR_ACENTO2),
            ("activos",     "🔄", "Préstamos activos",   COLOR_NARANJA),
            ("vencidos",    "⚠",  "Préstamos vencidos",  COLOR_PELIGRO),
        ]
        for clave, icono, etiqueta, color in definiciones:
            c = tarjeta(fila)
            c.pack(side="left", expand=True, fill="both", padx=(0, 16), pady=4)
            tk.Label(c, text=icono, font=("Segoe UI", 24),
                     bg=COLOR_BLANCO, fg=color).pack(pady=(18, 4))
            lbl_num = tk.Label(c, text="—", font=("Segoe UI", 28, "bold"),
                               bg=COLOR_BLANCO, fg=color)
            lbl_num.pack()
            tk.Label(c, text=etiqueta, font=FUENTE_PEQUEÑA,
                     bg=COLOR_BLANCO, fg=COLOR_TEXTO_SUAVE).pack(pady=(2, 18))
            self.cards[clave] = lbl_num

        # Tabla de préstamos vencidos
        tk.Label(self, text="Préstamos vencidos", font=FUENTE_SECCION,
                 bg=COLOR_FONDO, fg=COLOR_PELIGRO).pack(anchor="w", padx=32, pady=(24, 8))

        marco = tk.Frame(self, bg=COLOR_FONDO)
        marco.pack(fill="both", expand=True, padx=32, pady=(0, 20))
        self.tabla_vencidos = hacer_tabla(marco, [
            ("id",      "ID Ejemplar",  110),
            ("titulo",  "Título",       220),
            ("usuario", "Usuario",      160),
            ("limite",  "Límite",        90),
            ("dias",    "Días vencido",  100),
        ], alto=6)

    def refrescar(self):
        from datetime import date
        bib = self.bib
        activos  = [p for p in bib._prestamos if p.activo]
        vencidos = [p for p in activos if p.vencido]

        self.cards["ejemplares"].config(text=str(len(bib._ejemplares)))
        self.cards["usuarios"].config(text=str(len(bib._usuarios)))
        self.cards["activos"].config(text=str(len(activos)))
        self.cards["vencidos"].config(text=str(len(vencidos)))

        self.tabla_vencidos.delete(*self.tabla_vencidos.get_children())
        for p in vencidos:
            dias = (date.today() - p.fecha_limite).days
            self.tabla_vencidos.insert("", "end", values=(
                p.ejemplar.id_ejemplar, p.ejemplar.titulo,
                p.usuario.nombre_completo, str(p.fecha_limite), f"{dias} días"
            ))


# ── EJEMPLARES ─────────────────────────────────────────────────────

class PantallaEjemplares(PantallaBase):
    CLAVE = "ejemplares"

    def _construir(self):
        # Encabezado + buscador
        cab = tk.Frame(self, bg=COLOR_FONDO)
        cab.pack(fill="x", padx=28, pady=(24, 8))
        tk.Label(cab, text="Ejemplares", font=FUENTE_TITULO,
                 bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(side="left")
        tk.Label(cab, text="Buscar:", font=FUENTE_PEQUEÑA,
                 bg=COLOR_FONDO, fg=COLOR_TEXTO_SUAVE).pack(side="left", padx=(24, 4))
        self.busqueda_var = tk.StringVar()
        self.busqueda_var.trace_add("write", lambda *_: self.refrescar())
        tk.Entry(cab, textvariable=self.busqueda_var, font=FUENTE_NORMAL,
                 relief="solid", bd=1, bg="#FAFAFA", fg=COLOR_TEXTO,
                 width=22).pack(side="left")

        cuerpo = tk.Frame(self, bg=COLOR_FONDO)
        cuerpo.pack(fill="both", expand=True, padx=28, pady=(0, 16))
        cuerpo.columnconfigure(0, weight=3)
        cuerpo.columnconfigure(1, weight=2)
        cuerpo.rowconfigure(0, weight=1)

        marco = tk.Frame(cuerpo, bg=COLOR_FONDO)
        marco.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.tabla = hacer_tabla(marco, [
            ("id",      "ID",        90), ("titulo",  "Título",   160),
            ("autor",   "Autor",    130), ("isbn",    "ISBN",     120),
            ("anio",    "Año",       50), ("paginas", "Páginas",   65),
            ("tipo",    "Tipo",      80), ("estado",  "Estado",    80),
        ], alto=15)
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)

        panel = tarjeta(cuerpo)
        panel.grid(row=0, column=1, sticky="nsew")
        nb = ttk.Notebook(panel)
        nb.pack(fill="both", expand=True, padx=8, pady=8)
        tab_alta = tk.Frame(nb, bg=COLOR_BLANCO)
        tab_mod  = tk.Frame(nb, bg=COLOR_BLANCO)
        nb.add(tab_alta, text="  Alta  ")
        nb.add(tab_mod,  text="  Modificar  ")
        self._construir_tab_alta(tab_alta)
        self._construir_tab_mod(tab_mod)

    def _construir_tab_alta(self, tab):
        f = tk.Frame(tab, bg=COLOR_BLANCO)
        f.pack(fill="both", expand=True, padx=16, pady=8)
        f.columnconfigure(0, weight=1)
        self.e_id     = campo(f, "ID / Código de barra", 0)
        self.e_titulo = campo(f, "Título",               2)
        self.e_autor  = campo(f, "Autor",                4)
        self.e_isbn   = campo(f, "ISBN",                 6)
        tk.Label(f, text="Año de publicación", font=FUENTE_PEQUEÑA,
                 bg=COLOR_BLANCO, fg=COLOR_TEXTO_SUAVE, anchor="w"
                 ).grid(row=8, column=0, sticky="w", pady=(6, 0))
        fap = tk.Frame(f, bg=COLOR_BLANCO)
        fap.grid(row=9, column=0, sticky="ew", pady=(2, 0))
        fap.columnconfigure(0, weight=1); fap.columnconfigure(2, weight=1)
        self.e_anio = tk.Entry(fap, font=FUENTE_NORMAL, relief="solid", bd=1, bg="#FAFAFA", fg=COLOR_TEXTO)
        self.e_anio.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        tk.Label(fap, text="Páginas", font=FUENTE_PEQUEÑA, bg=COLOR_BLANCO,
                 fg=COLOR_TEXTO_SUAVE).grid(row=0, column=1, padx=4)
        self.e_paginas = tk.Entry(fap, font=FUENTE_NORMAL, relief="solid", bd=1,
                                  bg="#FAFAFA", fg=COLOR_TEXTO, width=6)
        self.e_paginas.grid(row=0, column=2, sticky="ew")
        tk.Label(f, text="Tipo", font=FUENTE_PEQUEÑA, bg=COLOR_BLANCO,
                 fg=COLOR_TEXTO_SUAVE, anchor="w").grid(row=10, column=0, sticky="w", pady=(6, 0))
        self.tipo_var = tk.StringVar(value="Prestable")
        mf = tk.Frame(f, bg=COLOR_BLANCO)
        mf.grid(row=11, column=0, sticky="w")
        for v in ("Prestable", "Consulta"):
            tk.Radiobutton(mf, text=v, variable=self.tipo_var, value=v,
                           font=FUENTE_NORMAL, bg=COLOR_BLANCO, fg=COLOR_TEXTO,
                           activebackground=COLOR_BLANCO, selectcolor=COLOR_BLANCO,
                           command=self._toggle_extra).pack(side="left", padx=(0, 10))
        self.lbl_extra = tk.Label(f, text="Días de préstamo", font=FUENTE_PEQUEÑA,
                                  bg=COLOR_BLANCO, fg=COLOR_TEXTO_SUAVE, anchor="w")
        self.lbl_extra.grid(row=12, column=0, sticky="w", pady=(6, 0))
        self.e_extra = tk.Entry(f, font=FUENTE_NORMAL, relief="solid", bd=1, bg="#FAFAFA", fg=COLOR_TEXTO)
        self.e_extra.grid(row=13, column=0, sticky="ew", pady=(2, 0))
        self.e_extra.insert(0, "7")
        bf = tk.Frame(f, bg=COLOR_BLANCO)
        bf.grid(row=14, column=0, sticky="ew", pady=(12, 0))
        boton(bf, "Registrar", self._registrar).pack(fill="x", pady=(0, 4))
        boton(bf, "Dar de baja (selección)", self._dar_baja, color=COLOR_PELIGRO).pack(fill="x")

    def _construir_tab_mod(self, tab):
        f = tk.Frame(tab, bg=COLOR_BLANCO)
        f.pack(fill="both", expand=True, padx=16, pady=8)
        f.columnconfigure(0, weight=1)
        tk.Label(f, text="Seleccioná un ejemplar\nen la tabla para editar.",
                 font=FUENTE_PEQUEÑA, bg=COLOR_BLANCO, fg=COLOR_TEXTO_SUAVE,
                 justify="left").grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.m_id = campo(f, "ID (no editable)", 1)
        self.m_id.config(state="disabled", bg="#EFEFEF")
        self.m_titulo  = campo(f, "Título",   3)
        self.m_autor   = campo(f, "Autor",    5)
        self.m_isbn    = campo(f, "ISBN",     7)
        self.m_anio    = campo(f, "Año",      9)
        self.m_paginas = campo(f, "Páginas", 11)
        boton(f, "Guardar cambios", self._modificar, color=COLOR_NARANJA
              ).grid(row=13, column=0, sticky="ew", pady=(14, 0))

    def _toggle_extra(self):
        if self.tipo_var.get() == "Prestable":
            self.lbl_extra.config(text="Días de préstamo")
            self.e_extra.delete(0, "end"); self.e_extra.insert(0, "7")
        else:
            self.lbl_extra.config(text="Sala de consulta")
            self.e_extra.delete(0, "end"); self.e_extra.insert(0, "Sala General")

    def _al_seleccionar(self, event):
        sel = self.tabla.selection()
        if not sel: return
        vals = self.tabla.item(sel[0])["values"]
        for e in (self.m_id, self.m_titulo, self.m_autor, self.m_isbn, self.m_anio, self.m_paginas):
            e.config(state="normal"); e.delete(0, "end")
        for e, v in zip((self.m_id, self.m_titulo, self.m_autor, self.m_isbn, self.m_anio, self.m_paginas),
                        (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5])):
            e.insert(0, v)
        self.m_id.config(state="disabled")

    def _registrar(self):
        id_ej  = self.e_id.get().strip(); titulo = self.e_titulo.get().strip()
        autor  = self.e_autor.get().strip(); isbn   = self.e_isbn.get().strip()
        extra  = self.e_extra.get().strip(); anio_s = self.e_anio.get().strip()
        pag_s  = self.e_paginas.get().strip()
        if not all([id_ej, titulo, autor, isbn, extra, anio_s, pag_s]):
            messagebox.showwarning("Campos incompletos", "Completá todos los campos."); return
        try:
            anio = int(anio_s); pag = int(pag_s)
        except ValueError:
            messagebox.showerror("Error", "Año y Páginas deben ser números enteros."); return
        try:
            if self.tipo_var.get() == "Prestable":
                ej = EjemplarPrestable(id_ej, titulo, autor, isbn, anio, pag, int(extra))
            else:
                ej = EjemplarConsulta(id_ej, titulo, autor, isbn, anio, pag, extra)
            self.bib.registrar_ejemplar(ej)
            messagebox.showinfo("✔ Registrado", f"Ejemplar '{id_ej}' registrado.")
            for e in (self.e_id, self.e_titulo, self.e_autor, self.e_isbn, self.e_anio, self.e_paginas):
                e.delete(0, "end")
            self.e_extra.delete(0, "end"); self.e_extra.insert(0, "7")
            self.refrescar_cb()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _modificar(self):
        self.m_id.config(state="normal")
        id_ej = self.m_id.get().strip()
        self.m_id.config(state="disabled")
        if not id_ej:
            messagebox.showwarning("Sin selección", "Seleccioná un ejemplar en la tabla."); return
        try:
            anio = int(self.m_anio.get()) if self.m_anio.get().strip() else None
            pag  = int(self.m_paginas.get()) if self.m_paginas.get().strip() else None
        except ValueError:
            messagebox.showerror("Error", "Año y Páginas deben ser números enteros."); return
        try:
            self.bib.modificar_ejemplar(id_ej,
                titulo=self.m_titulo.get().strip() or None,
                autor=self.m_autor.get().strip() or None,
                isbn=self.m_isbn.get().strip() or None,
                anio_publicacion=anio, cantidad_paginas=pag)
            messagebox.showinfo("✔ Modificado", f"Ejemplar '{id_ej}' actualizado.")
            self.refrescar_cb()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _dar_baja(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Seleccioná un ejemplar en la tabla."); return
        id_ej = self.tabla.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirmar baja", f"¿Dar de baja '{id_ej}'?"):
            try:
                self.bib.dar_baja_ejemplar(str(id_ej))
                messagebox.showinfo("✔ Baja", f"Ejemplar '{id_ej}' dado de baja.")
                self.refrescar_cb()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def refrescar(self):
        filtro = self.busqueda_var.get().lower()
        self.tabla.delete(*self.tabla.get_children())
        for ej in self.bib._ejemplares:
            if filtro and filtro not in ej.titulo.lower() and filtro not in ej.autor.lower() and filtro not in ej.isbn.lower():
                continue
            tipo   = "Prestable" if isinstance(ej, EjemplarPrestable) else "Consulta"
            estado = ej.estado if isinstance(ej, EjemplarPrestable) else ej.sala
            iid = self.tabla.insert("", "end", values=(
                ej.id_ejemplar, ej.titulo, ej.autor, ej.isbn,
                ej.anio_publicacion, ej.cantidad_paginas, tipo, estado))
            # Color de estado
            if isinstance(ej, EjemplarPrestable):
                if ej.estado == "prestado":
                    self.tabla.item(iid, tags=("prestado",))
                else:
                    self.tabla.item(iid, tags=("disponible",))
        self.tabla.tag_configure("prestado",    foreground="#E05C5C")
        self.tabla.tag_configure("disponible",  foreground="#2A9D6E")


# ── USUARIOS ───────────────────────────────────────────────────────

class PantallaUsuarios(PantallaBase):
    CLAVE = "usuarios"

    def _construir(self):
        cab = tk.Frame(self, bg=COLOR_FONDO)
        cab.pack(fill="x", padx=28, pady=(24, 8))
        tk.Label(cab, text="Usuarios", font=FUENTE_TITULO,
                 bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(side="left")
        tk.Label(cab, text="Buscar:", font=FUENTE_PEQUEÑA,
                 bg=COLOR_FONDO, fg=COLOR_TEXTO_SUAVE).pack(side="left", padx=(24, 4))
        self.busqueda_var = tk.StringVar()
        self.busqueda_var.trace_add("write", lambda *_: self.refrescar())
        tk.Entry(cab, textvariable=self.busqueda_var, font=FUENTE_NORMAL,
                 relief="solid", bd=1, bg="#FAFAFA", fg=COLOR_TEXTO,
                 width=22).pack(side="left")

        cuerpo = tk.Frame(self, bg=COLOR_FONDO)
        cuerpo.pack(fill="both", expand=True, padx=28, pady=(0, 16))
        cuerpo.columnconfigure(0, weight=3); cuerpo.columnconfigure(1, weight=2)
        cuerpo.rowconfigure(0, weight=1)

        marco = tk.Frame(cuerpo, bg=COLOR_FONDO)
        marco.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.tabla = hacer_tabla(marco, [
            ("nombre",   "Nombre",   120), ("apellido", "Apellido",  120),
            ("dni",      "DNI",      100), ("email",    "Email",     180),
            ("prestamos","Préstamos activos", 120),
        ], alto=15)
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)

        panel = tarjeta(cuerpo)
        panel.grid(row=0, column=1, sticky="nsew")
        nb = ttk.Notebook(panel)
        nb.pack(fill="both", expand=True, padx=8, pady=8)
        tab_alta = tk.Frame(nb, bg=COLOR_BLANCO)
        tab_mod  = tk.Frame(nb, bg=COLOR_BLANCO)
        nb.add(tab_alta, text="  Alta  ")
        nb.add(tab_mod,  text="  Modificar  ")
        self._construir_tab_alta(tab_alta)
        self._construir_tab_mod(tab_mod)

    def _construir_tab_alta(self, tab):
        f = tk.Frame(tab, bg=COLOR_BLANCO)
        f.pack(fill="both", expand=True, padx=16, pady=8)
        f.columnconfigure(0, weight=1)
        self.e_nombre   = campo(f, "Nombre",   0)
        self.e_apellido = campo(f, "Apellido", 2)
        self.e_dni      = campo(f, "DNI",      4)
        self.e_email    = campo(f, "Email",    6)
        bf = tk.Frame(f, bg=COLOR_BLANCO)
        bf.grid(row=8, column=0, sticky="ew", pady=(14, 0))
        boton(bf, "Registrar", self._registrar).pack(fill="x", pady=(0, 4))
        boton(bf, "Dar de baja (selección)", self._dar_baja, color=COLOR_PELIGRO).pack(fill="x")

    def _construir_tab_mod(self, tab):
        f = tk.Frame(tab, bg=COLOR_BLANCO)
        f.pack(fill="both", expand=True, padx=16, pady=8)
        f.columnconfigure(0, weight=1)
        tk.Label(f, text="Seleccioná un usuario\nen la tabla para editar.",
                 font=FUENTE_PEQUEÑA, bg=COLOR_BLANCO, fg=COLOR_TEXTO_SUAVE,
                 justify="left").grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.m_dni      = campo(f, "DNI (no editable)", 1)
        self.m_dni.config(state="disabled", bg="#EFEFEF")
        self.m_nombre   = campo(f, "Nombre",   3)
        self.m_apellido = campo(f, "Apellido", 5)
        self.m_email    = campo(f, "Email",    7)
        boton(f, "Guardar cambios", self._modificar, color=COLOR_NARANJA
              ).grid(row=9, column=0, sticky="ew", pady=(14, 0))

    def _al_seleccionar(self, event):
        sel = self.tabla.selection()
        if not sel: return
        vals = self.tabla.item(sel[0])["values"]
        for e in (self.m_dni, self.m_nombre, self.m_apellido, self.m_email):
            e.config(state="normal"); e.delete(0, "end")
        self.m_nombre.insert(0, vals[0]); self.m_apellido.insert(0, vals[1])
        self.m_dni.insert(0, vals[2]);    self.m_email.insert(0, vals[3])
        self.m_dni.config(state="disabled")

    def _registrar(self):
        nombre = self.e_nombre.get().strip(); apellido = self.e_apellido.get().strip()
        dni    = self.e_dni.get().strip();    email    = self.e_email.get().strip()
        if not all([nombre, apellido, dni, email]):
            messagebox.showwarning("Campos incompletos", "Completá todos los campos."); return
        try:
            self.bib.registrar_usuario(Usuario(nombre, apellido, dni, email))
            messagebox.showinfo("✔ Registrado", f"Usuario '{nombre} {apellido}' registrado.")
            for e in (self.e_nombre, self.e_apellido, self.e_dni, self.e_email): e.delete(0, "end")
            self.refrescar_cb()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _modificar(self):
        self.m_dni.config(state="normal")
        dni = self.m_dni.get().strip()
        self.m_dni.config(state="disabled")
        if not dni:
            messagebox.showwarning("Sin selección", "Seleccioná un usuario en la tabla."); return
        try:
            self.bib.modificar_usuario(dni,
                nombre=self.m_nombre.get().strip() or None,
                apellido=self.m_apellido.get().strip() or None,
                email=self.m_email.get().strip() or None)
            messagebox.showinfo("✔ Modificado", "Usuario actualizado correctamente.")
            self.refrescar_cb()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _dar_baja(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Seleccioná un usuario en la tabla."); return
        dni = str(self.tabla.item(sel[0])["values"][2])
        if messagebox.askyesno("Confirmar baja", f"¿Dar de baja al usuario con DNI '{dni}'?"):
            try:
                self.bib.dar_baja_usuario(dni)
                messagebox.showinfo("✔ Baja", "Usuario dado de baja.")
                self.refrescar_cb()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def refrescar(self):
        filtro = self.busqueda_var.get().lower()
        self.tabla.delete(*self.tabla.get_children())
        for u in self.bib._usuarios:
            if filtro and filtro not in u.nombre.lower() and filtro not in u.apellido.lower() and filtro not in u.dni:
                continue
            self.tabla.insert("", "end", values=(
                u.nombre, u.apellido, u.dni, u.email, len(u.prestamos_activos)))


# ── PRÉSTAMOS ──────────────────────────────────────────────────────

class PantallaPrestamos(PantallaBase):
    CLAVE = "prestamos"

    def _construir(self):
        tk.Label(self, text="Préstamos", font=FUENTE_TITULO,
                 bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(anchor="w", padx=28, pady=(24, 8))

        cuerpo = tk.Frame(self, bg=COLOR_FONDO)
        cuerpo.pack(fill="both", expand=True, padx=28, pady=(0, 16))
        cuerpo.columnconfigure(0, weight=3); cuerpo.columnconfigure(1, weight=2)
        cuerpo.rowconfigure(0, weight=1)

        marco = tk.Frame(cuerpo, bg=COLOR_FONDO)
        marco.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.tabla = hacer_tabla(marco, [
            ("id_ej",   "ID Ejemplar", 100), ("titulo",  "Título",  170),
            ("usuario", "Usuario",     140), ("inicio",  "Desde",    90),
            ("limite",  "Límite",       90), ("estado",  "Estado",   90),
        ], alto=15)
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)

        panel = tarjeta(cuerpo)
        panel.grid(row=0, column=1, sticky="nsew")
        f = tk.Frame(panel, bg=COLOR_BLANCO)
        f.pack(fill="both", expand=True, padx=16, pady=12)
        f.columnconfigure(0, weight=1)

        tk.Label(f, text="Nuevo préstamo", font=FUENTE_SECCION,
                 bg=COLOR_BLANCO, fg=COLOR_TEXTO).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.e_id_ej = campo(f, "ID del ejemplar", 1)
        self.e_dni   = campo(f, "DNI del usuario", 3)
        boton(f, "Registrar préstamo", self._prestar, color=COLOR_ACENTO2
              ).grid(row=5, column=0, sticky="ew", pady=(12, 0))

        ttk.Separator(f, orient="horizontal").grid(row=6, column=0, sticky="ew", pady=16)

        tk.Label(f, text="Devolución", font=FUENTE_SECCION,
                 bg=COLOR_BLANCO, fg=COLOR_TEXTO).grid(row=7, column=0, sticky="w", pady=(0, 4))
        self.e_id_dev = campo(f, "ID del ejemplar a devolver", 8)
        boton(f, "Registrar devolución", self._devolver, color=COLOR_PELIGRO
              ).grid(row=10, column=0, sticky="ew", pady=(12, 0))
        tk.Label(f, text="Hacé clic en un préstamo activo\npara autocompletar el ID.",
                 font=FUENTE_PEQUEÑA, bg=COLOR_BLANCO, fg=COLOR_TEXTO_SUAVE,
                 justify="center").grid(row=11, column=0, pady=(12, 0))

    def _al_seleccionar(self, event):
        sel = self.tabla.selection()
        if sel:
            id_ej = self.tabla.item(sel[0])["values"][0]
            self.e_id_dev.delete(0, "end"); self.e_id_dev.insert(0, str(id_ej))

    def _prestar(self):
        id_ej = self.e_id_ej.get().strip(); dni = self.e_dni.get().strip()
        if not all([id_ej, dni]):
            messagebox.showwarning("Campos incompletos", "Completá el ID y el DNI."); return
        try:
            self.bib.prestar_ejemplar(id_ej, dni)
            messagebox.showinfo("✔ Préstamo registrado", f"Ejemplar '{id_ej}' prestado correctamente.")
            self.e_id_ej.delete(0, "end"); self.e_dni.delete(0, "end")
            self.refrescar_cb()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _devolver(self):
        id_ej = self.e_id_dev.get().strip()
        if not id_ej:
            messagebox.showwarning("Campo vacío", "Ingresá el ID del ejemplar."); return
        try:
            self.bib.devolver_ejemplar(id_ej)
            messagebox.showinfo("✔ Devolución registrada", f"Ejemplar '{id_ej}' devuelto correctamente.")
            self.e_id_dev.delete(0, "end"); self.refrescar_cb()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def refrescar(self):
        self.tabla.delete(*self.tabla.get_children())
        for p in self.bib._prestamos:
            estado = "Activo" if p.activo else "Devuelto"
            if p.vencido: estado = "⚠ Vencido"
            iid = self.tabla.insert("", "end", values=(
                p.ejemplar.id_ejemplar, p.ejemplar.titulo,
                p.usuario.nombre_completo, str(p.fecha_inicio),
                str(p.fecha_limite), estado))
            if p.vencido:
                self.tabla.item(iid, tags=("vencido",))
            elif not p.activo:
                self.tabla.item(iid, tags=("devuelto",))
        self.tabla.tag_configure("vencido",  foreground=COLOR_PELIGRO)
        self.tabla.tag_configure("devuelto", foreground=COLOR_TEXTO_SUAVE)


if __name__ == "__main__":
    app = App()
    app.mainloop()
