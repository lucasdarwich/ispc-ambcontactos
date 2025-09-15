import mysql.connector

class ConexionDB:
    """
    Clase para manejar la conexión a una base de datos MySQL.
    """
    def __init__(self, host, user, password, database):
        """
        Inicializa la conexión a la base de datos.
        """
        try:
            self.conexion = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            if self.conexion.is_connected():
                self.cursor = self.conexion.cursor()
                print("✅ Conexión exitosa a la base de datos")
        except mysql.connector.Error as e:
            print(f"❌ Error al conectar: {e}")

    def cerrar(self):
        """
        Cierra la conexión a la base de datos.
        """
        if self.conexion.is_connected():
            self.conexion.close()
            print("🔒 Conexión cerrada")


class Contactos:
    """
    Clase para manejar operaciones CRUD en la tabla Contactos.
    """
    def __init__(self, conexion_db):
        
        self.conexion_db = conexion_db

    def agregar(self, nombre, apellido, telefono, email):
        """
        Agrega un nuevo contacto a la base de datos.
        """
        sql = "INSERT INTO Contactos (Nombre, Apellido, Telefono, Email) VALUES (%s, %s, %s, %s)"
        valores = (nombre, apellido, telefono, email)
        self.conexion_db.cursor.execute(sql, valores)
        self.conexion_db.conexion.commit()
        print("✅ Contacto agregado")

    def listar(self):
        """
        Lista todos los contactos en la base de datos.
        """
        self.conexion_db.cursor.execute("SELECT * FROM Contactos")
        resultados = self.conexion_db.cursor.fetchall()
        return resultados
    
    def actualizar(self, id_contacto, nombre=None, apellido=None, telefono=None, email=None):
        """
        Actualiza un contacto existente en la base de datos. 
        si no hay parametros para actualizar, retorna 0
        """ 
        sets = []
        valores = []

        if nombre not in (None, ""):
            sets.append("Nombre=%s")
            valores.append(nombre)
        if apellido not in (None, ""):
            sets.append("Apellido=%s")
            valores.append(apellido)
        if telefono not in (None, ""):
            sets.append("Telefono=%s")
            valores.append(telefono)
        if email not in (None, ""):
            sets.append("Email=%s")
            valores.append(email)

        if not sets:
            return 0  # nada para actualizar

        sql = "UPDATE Contactos SET " + ", ".join(sets) + " WHERE idContacto=%s"
        valores.append(id_contacto)
        self.conexion_db.cursor.execute(sql, tuple(valores))
        self.conexion_db.conexion.commit()
        return self.conexion_db.cursor.rowcount


    def eliminar(self, id_contacto):
        """
        Elimina un contacto por ID de la base de datos.
        """
        sql = "DELETE FROM Contactos WHERE idContacto=%s"
        self.conexion_db.cursor.execute(sql, (id_contacto,))
        self.conexion_db.conexion.commit()
        print("🗑️ Contacto eliminado")
