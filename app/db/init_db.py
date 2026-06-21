import os
from sqlalchemy import text
from app.db.database import engine

def inicializar_base_de_datos():
    ruta_sql = os.path.abspath(os.path.join(os.path.dirname(__file__), 'schema.sql'))
    
    print(f"Buscando el archivo de inicializacion en {ruta_sql}")
    
    if not os.path.exists(ruta_sql):
        print("Error: No se encontró el archivo schema.sql")
        return
    
    with open(ruta_sql, 'r', encoding='utf-8') as archivo:
        queries_sql = archivo.read()
        
    try:
        with engine.connect() as conexion:
            print("Conectando a PostgreSQL...")
            conexion.execute(text(queries_sql))
            conexion.commit()
        print("Base de datos inicializada correctamente.")
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")

if __name__ == "__main__":
    print("Iniciando el script de inicialización...")  # Primera prueba de vida
    try:
        inicializar_base_de_datos()
    except Exception as e:
        print(f"Se interrumpió la ejecución bruscamente: {e}")