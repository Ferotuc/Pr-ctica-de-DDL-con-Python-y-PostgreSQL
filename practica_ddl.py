
import psycopg2

# --- Configura tu conexión aquí ---
CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "postgres",   # puedes usar otra DB si lo deseas
    "user": "postgres",     # usuario por defecto del contenedor postgres
    "password": "fernando"  # <--- tu contraseña
}

def run(cur, descripcion, sql):
    print(f"\n▶ {descripcion}")
    try:
        cur.execute(sql)
        print("✓ OK")
    except Exception as e:
        # Para fines didácticos, continuamos si algo ya existe, etc.
        msg = str(e)
        if "already exists" in msg or "does not exist" in msg or "duplicate" in msg:
            print(f"… Aviso: {msg}")
        else:
            raise

def ver_columnas(cur, tabla):
    print(f"\n📋 Columnas en {tabla}:")
    cur.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position;
    """, (tabla,))
    rows = cur.fetchall()
    for r in rows:
        print(f" - {r[0]:20s} {r[1]:12s} NULLABLE={r[2]}")

def ver_restricciones(cur, tabla):
    print(f"\n🔒 Restricciones en {tabla}:")
    cur.execute("""
        SELECT c.conname, pg_get_constraintdef(c.oid)
        FROM pg_constraint c
        JOIN pg_class t ON c.conrelid = t.oid
        WHERE t.relname = %s
        ORDER BY c.conname;
    """, (tabla,))
    rows = cur.fetchall()
    if not rows:
        print(" (ninguna)")
    for name, defn in rows:
        print(f" - {name}: {defn}")

def main():
    print("Conectando a PostgreSQL…")
    conn = psycopg2.connect(**CONFIG)
    conn.autocommit = True  # Para DDL es cómodo
    with conn.cursor() as cur:
        # 1) Crear al menos 2 tablas
        run(cur, "Crear tabla clientes",
            """
            CREATE TABLE IF NOT EXISTS clientes (
                cliente_id  SERIAL PRIMARY KEY,
                nombre      VARCHAR(100) NOT NULL,
                email       VARCHAR(200) UNIQUE
            );
            """
        )

        run(cur, "Crear tabla productos",
            """
            CREATE TABLE IF NOT EXISTS productos (
                producto_id SERIAL PRIMARY KEY,
                nombre      VARCHAR(100) NOT NULL,
                precio      NUMERIC(10,2) NOT NULL CHECK (precio >= 0)
            );
            """
        )

        # 2) DDL: Agregar columna nueva
        run(cur, "Agregar columna 'telefono' en clientes",
            "ALTER TABLE clientes ADD COLUMN IF NOT EXISTS telefono VARCHAR(20);"
        )

        # 3) DDL: Renombrar columna
        run(cur, "Renombrar columna 'telefono' -> 'telefono_movil' en clientes",
            "ALTER TABLE clientes RENAME COLUMN telefono TO telefono_movil;"
        )

        # 4) DDL: Eliminar columna
        run(cur, "Eliminar columna 'telefono_movil' en clientes",
            "ALTER TABLE clientes DROP COLUMN IF EXISTS telefono_movil;"
        )

        # 5) DDL: Agregar un CHECK (restricción) sobre una columna
        run(cur, "Agregar columna 'edad' en clientes (si no existe)",
            "ALTER TABLE clientes ADD COLUMN IF NOT EXISTS edad INT;"
        )

        print("\n▶ Agregar restricción CHECK 'chk_clientes_edad' (0..120) en clientes")
        try:
            cur.execute("ALTER TABLE clientes ADD CONSTRAINT chk_clientes_edad CHECK (edad BETWEEN 0 AND 120);")
            print("✓ OK")
        except Exception as e:
            # Postgres no siempre soporta IF NOT EXISTS en ADD CONSTRAINT; atrapamos si ya existe
            if "already exists" in str(e):
                print("… Aviso: la restricción ya existía, se omite")
            else:
                raise

        # 6) DDL extra: Renombrar una columna en otra tabla
        run(cur, "Renombrar columna 'nombre' -> 'nombre_producto' en productos",
            "ALTER TABLE productos RENAME COLUMN nombre TO nombre_producto;"
        )

        # 7) DDL: Eliminar una tabla (creamos una temporal para demostrar)
        run(cur, "Crear tabla temporal 'tmp_a_eliminar'",
            "CREATE TABLE IF NOT EXISTS tmp_a_eliminar (id SERIAL PRIMARY KEY);"
        )
        run(cur, "Eliminar tabla temporal 'tmp_a_eliminar'",
            "DROP TABLE IF EXISTS tmp_a_eliminar;"
        )

        # Mostrar resultados
        ver_columnas(cur, "clientes")
        ver_restricciones(cur, "clientes")
        ver_columnas(cur, "productos")
        ver_restricciones(cur, "productos")

    conn.close()
    print("\nListo.")

if __name__ == "__main__":
    main()
