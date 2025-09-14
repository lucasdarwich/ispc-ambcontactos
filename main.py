import tkinter as tk
from tkinter import messagebox, ttk
from clases import ConexionDB, Contactos  # tus clases
import os
from dotenv import load_dotenv
# Cargar variables de entorno desde .env

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

class App:
    def __init__(self, root):
        """
        Inicializamos la interfaz gráfica y sus componentes.
        """
        self.root = root
        self.root.title("Gestión de Contactos")
        self.root.geometry("700x480")

        """
        Sin conexión al inicio de la App
        """
        self.db = None
        self.contactos = None

        """
        Campos de entrada Label + Entry
        """
        tk.Label(root, text="Nombre:").grid(row=0, column=0, padx=6, pady=6, sticky="e")
        self.entry_nombre = tk.Entry(root, width=24)
        self.entry_nombre.grid(row=0, column=1, padx=6, pady=6, sticky="w")

        tk.Label(root, text="Apellido:").grid(row=0, column=2, padx=6, pady=6, sticky="e")
        self.entry_apellido = tk.Entry(root, width=24)
        self.entry_apellido.grid(row=0, column=3, padx=6, pady=6, sticky="w")

        tk.Label(root, text="Teléfono:").grid(row=1, column=0, padx=6, pady=6, sticky="e")
        self.entry_telefono = tk.Entry(root, width=24)
        self.entry_telefono.grid(row=1, column=1, padx=6, pady=6, sticky="w")

        tk.Label(root, text="Correo:").grid(row=1, column=2, padx=6, pady=6, sticky="e")
        self.entry_email = tk.Entry(root, width=24)
        self.entry_email.grid(row=1, column=3, padx=6, pady=6, sticky="w")

        """ Botones"""
        self.btn_conectar = tk.Button(root, text="Conectar", command=self.conectar)
        self.btn_conectar.grid(row=0, column=4, padx=6, pady=6)

        self.btn_desconectar = tk.Button(root, text="Desconectar", command=self.desconectar)
        self.btn_desconectar.grid(row=1, column=4, padx=6, pady=6)

        self.btn_agregar = tk.Button(root, text="Agregar", command=self.agregar)
        self.btn_agregar.grid(row=2, column=0, padx=6, pady=6, sticky="w")

        self.btn_actualizar = tk.Button(root, text="Actualizar (según selección)", command=self.actualizar)
        self.btn_actualizar.grid(row=2, column=1, padx=6, pady=6, sticky="w")

        self.btn_mostrar = tk.Button(root, text="Refrescar", command=self.refrescar)
        self.btn_mostrar.grid(row=2, column=2, padx=6, pady=6, sticky="w")

        """
        Tabla para mostrar contactos
        Treeview con Scrollbar
        """
        cols = ("ID", "Nombre", "Apellido", "Teléfono", "Correo")
        self.tree = ttk.Treeview(root, columns=cols, show="headings", height=12)
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.column("ID", width=60, anchor="center")
        self.tree.column("Nombre", width=150)
        self.tree.column("Apellido", width=150)
        self.tree.column("Teléfono", width=120)
        self.tree.column("Correo", width=200)

        self.tree.grid(row=3, column=0, columnspan=5, padx=10, pady=10, sticky="nsew")

        """
        Scrollbar vertical para la tabla de contactos
        """
        vsb = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        vsb.grid(row=3, column=5, sticky="ns", padx=(0,10), pady=10)

        """ 
        Evento al seleccionar fila en la tabla y cargar en los campos en la parte superior
        """
        self.tree.bind("<<TreeviewSelect>>", self._on_select_row)

        """ 
        Frame para eliminar contacto por ID abajo de la tabla
        """
        frm_del = tk.Frame(root)
        frm_del.grid(row=4, column=0, columnspan=5, padx=10, pady=6, sticky="w")

        tk.Label(frm_del, text="Si desea eliminar un contacto, indique su ID:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_id = tk.Entry(frm_del, width=10)
        self.entry_id.grid(row=0, column=1, padx=5, pady=5)
        self.btn_eliminar = tk.Button(frm_del, text="Eliminar", command=self.eliminar)
        self.btn_eliminar.grid(row=0, column=2, padx=5, pady=5)

        """
        Gird weights para que las columnas y filas de la tabla crezcan con la ventana
        """
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_columnconfigure(3, weight=1)

        # Deshabilitar acciones hasta conectarse
        self._set_connected(False)

        # Atajo F5 para refrescar
        self.root.bind("<F5>", lambda e: self.refrescar())

    def _set_connected(self, connected: bool):
        """ 
        Habilitamos o deshabilitamos botones según estado de conexión 
        """
        state_crud = "normal" if connected else "disabled"
        """
        Botones CRUD
        """
        self.btn_agregar.config(state=state_crud)
        self.btn_actualizar.config(state=state_crud)
        self.btn_mostrar.config(state=state_crud)
        self.btn_eliminar.config(state=state_crud)
        """
        Botones Conexión
        """
        self.btn_conectar.config(state=("disabled" if connected else "normal"))
        self.btn_desconectar.config(state=("normal" if connected else "disabled"))

    # ---------------- Conexión ----------------
    def conectar(self):
        """
        Conecta a la base de datos y habilita los botones CRUD.
        Usa datos del archivo .env
        """
        try:
            self.db = ConexionDB(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
            self.contactos = Contactos(self.db)
            self._set_connected(True)
            messagebox.showinfo("Conexión", "✅ Conectado a la base de datos")
            self.mostrar()
        except Exception as e:
            self.db = None
            self.contactos = None
            self._set_connected(False)
            messagebox.showerror("Error", f"No se pudo conectar: {e}")

    def desconectar(self):
        """
        Desconecta de la base de datos y deshabilita los botones CRUD.
        """
        if self.db:
            try:
                self.db.cerrar()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cerrar la conexión:\n{e}")
        self.db = None
        self.contactos = None
        self._set_connected(False)
        self._limpiar_tabla()
        self._limpiar_inputs()
        messagebox.showinfo("Conexión", "🔒 Desconectado de la base de datos")

    def _limpiar_tabla(self):
        """ 
        Limpia todas las filas de la tabla.
        """
        for row in self.tree.get_children():
            self.tree.delete(row)

    def _limpiar_inputs(self):
        """ 
        Limpia todos los campos de entrada (incluido ID de eliminación).
        """
        for e in (self.entry_nombre, self.entry_apellido, self.entry_telefono, self.entry_email, self.entry_id):
            e.delete(0, tk.END)

    def _on_select_row(self, event):
        """Se ejecuta al seleccionar una fila en la tabla.
        Carga los datos en los campos de entrada para facilitar la edición."""
        sel = self.tree.selection()
        if not sel:
            return
        valores = self.tree.item(sel[0], "values")
        self.entry_nombre.delete(0, tk.END)
        self.entry_nombre.insert(0, valores[1])
        self.entry_apellido.delete(0, tk.END)
        self.entry_apellido.insert(0, valores[2])
        self.entry_telefono.delete(0, tk.END)
        self.entry_telefono.insert(0, valores[3])
        self.entry_email.delete(0, tk.END)
        self.entry_email.insert(0, valores[4])

    def _requiere_conexion(self):
        """ Verifica que haya conexión a la base de datos """
        if not self.contactos:
            messagebox.showwarning("Advertencia", "No hay conexión a la BD")
            return False
        return True

    # --------------- Acciones -----------------
    def mostrar(self):
        """ Muestra todos los contactos en la tabla. """
        if not self._requiere_conexion():
            return
        self._limpiar_tabla()
        try:
            for fila in self.contactos.listar():
                self.tree.insert("", tk.END, values=fila)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los contactos:\n{e}")

    def refrescar(self):
        """ Limpia campos y vuelve a mostrar todos los contactos. """
        if not self._requiere_conexion():
            return
        self._limpiar_inputs()
        for sel in self.tree.selection():
            self.tree.selection_remove(sel)
        self.mostrar()

    def agregar(self):
        """ Agrega un nuevo contacto. """
        if not self._requiere_conexion():
            return
        nombre = self.entry_nombre.get().strip()
        apellido = self.entry_apellido.get().strip()
        telefono = self.entry_telefono.get().strip()
        email = self.entry_email.get().strip()

        if not nombre or not apellido:
            return messagebox.showwarning("Datos faltantes", "Nombre y Apellido son obligatorios.")

        try:
            self.contactos.agregar(nombre, apellido, telefono, email)
            messagebox.showinfo("OK", "Contacto agregado.")
            self.refrescar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar el contacto:\n{e}")

    def actualizar(self):
        """ Actualiza el contacto seleccionado en la tabla. """
        if not self._requiere_conexion():
            return
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Seleccionar", "Seleccioná un contacto en la tabla para actualizar.")
        id_sel = self.tree.item(sel[0], "values")[0]

        nombre   = self.entry_nombre.get().strip() or None
        apellido = self.entry_apellido.get().strip() or None
        telefono = self.entry_telefono.get().strip() or None
        email    = self.entry_email.get().strip() or None

        try:
            filas = self.contactos.actualizar(int(id_sel), nombre=nombre, apellido=apellido, telefono=telefono, email=email)
            if filas == 0:
                messagebox.showinfo("Info", "No hubo cambios.")
            else:
                messagebox.showinfo("OK", "Contacto actualizado.")
            self.refrescar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el contacto:\n{e}")

    def eliminar(self):
        """ Elimina el contacto cuyo ID se indica en el campo ID. """
        if not self._requiere_conexion():
            return
        id_txt = self.entry_id.get().strip()
        if not id_txt.isdigit():
            return messagebox.showwarning("Dato inválido", "Ingresá un ID numérico para eliminar.")
        try:
            filas = self.contactos.eliminar(int(id_txt))
            if filas == 0:
                messagebox.showinfo("Info", "No se encontró el ID indicado.")
            else:
                messagebox.showinfo("OK", "Contacto eliminado.")
            self.refrescar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el contacto:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
