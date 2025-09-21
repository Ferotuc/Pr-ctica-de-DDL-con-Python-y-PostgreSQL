
# Práctica DDL con Python + PostgreSQL (Docker)

Este README te guía paso a paso para:
- Conectarte desde Python a PostgreSQL (contenedor Docker).
- Crear **al menos 2 tablas** desde Python.
- Ejecutar DDL: **agregar columna**, **renombrar columna**, **eliminar columna**, **agregar CHECK** y **eliminar una tabla**.

## 0) Verifica que tu contenedor está corriendo
```bash
docker ps
# Debes ver algo como: postgres-db  ...  0.0.0.0:5432->5432/tcp
```

Si no está iniciado:
```bash
docker start postgres-db
```

> **Datos por defecto** de tu contenedor (con el run que usaste):
> - Usuario: `postgres`
> - Contraseña: `fernando`
> - Puerto: `5432`
> - Base de datos: `postgres`

## 1) Instala el driver de PostgreSQL para Python
En **VS Code** abre la terminal integrada (Ctrl+ñ) y asegúrate de usar el **mismo intérprete** que tienes seleccionado en VS Code.
```bash
py -3.11 -m pip install --upgrade pip
py -3.11 -m pip install psycopg2-binary
# Alternativa:
# python -m pip install psycopg2-binary
```

Comprueba que quedó instalado en ese intérprete:
```bash
py -3.11 -c "import sys, psycopg2; print(sys.executable); print(psycopg2.__version__)"
```

## 2) Descarga este repo/archivos
Copia `practica_ddl.py` junto a tu proyecto en VS Code.

## 3) Ejecuta el script
```bash
py -3.11 practica_ddl.py
# o
python practica_ddl.py
```

Deberías ver salidas del tipo:
```
Conectando a PostgreSQL…
▶ Crear tabla clientes
✓ OK
▶ Crear tabla productos
✓ OK
▶ Agregar columna 'telefono' en clientes
✓ OK
...
📋 Columnas en clientes:
 - cliente_id           integer      NULLABLE=NO
 - nombre               character varying NULLABLE=NO
 - email                character varying NULLABLE=YES
 - edad                 integer      NULLABLE=YES

🔒 Restricciones en clientes:
 - clientes_pkey: PRIMARY KEY (cliente_id)
 - chk_clientes_edad: CHECK ((edad >= 0) AND (edad <= 120))
```

## 4) ¿Cómo verifico desde `psql`?
Puedes entrar al `psql` dentro del contenedor:
```bash
docker exec -it postgres-db psql -U postgres -d postgres
\dt
\d clientes
\d productos
\q
```

## 5) Errores comunes
- **ModuleNotFoundError: No module named 'psycopg2'**  
  Instala `psycopg2-binary` en el **mismo** Python que usas al ejecutar el script (revisa `python: Select Interpreter` en VS Code y usa `py -3.11 -m pip ...`).

- **Fallo de conexión (timeout)**  
  Asegúrate de que el contenedor está **running** y que el puerto `5432` está mapeado a `localhost:5432`.  
  `docker ps` debe mostrar `0.0.0.0:5432->5432/tcp`.

- **"already exists" / "does not exist"**  
  Son mensajes informativos cuando repites el script. Para la práctica está bien; el script los captura y continúa.

## 6) ¿Qué operaciones DDL hace el script?
1. Crea tablas `clientes` y `productos`.
2. **ADD COLUMN**: `telefono` (y luego la elimina para mostrar `DROP COLUMN`).  
3. **RENAME COLUMN**: renombra `telefono` → `telefono_movil` y `nombre` → `nombre_producto`.  
4. **DROP COLUMN**: elimina `telefono_movil`.  
5. **ADD CHECK**: `chk_clientes_edad` valida que `edad` ∈ [0,120].  
6. **DROP TABLE**: crea `tmp_a_eliminar` y luego la elimina.

¡Eso cumple con todos los requisitos de la práctica!
