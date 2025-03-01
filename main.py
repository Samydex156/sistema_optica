import os
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import mysql.connector

app = FastAPI()

# Configurar la conexión a MySQL
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),  # Cambia esto si usas otro usuario
        password=os.getenv("password"),  # Cambia esto por tu contraseña
        database=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT","3306"))
    )

# Montar la carpeta "static" para archivos CSS/JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar Jinja2 para las plantillas HTML
templates = Jinja2Templates(directory="templates")

# Página principal (registrar productos)
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Endpoint para agregar un producto
@app.post("/agregar-producto")
async def agregar_producto(nombre: str = Form(...), precio: float = Form(...), cantidad: int = Form(...)):
    db = get_db_connection()
    cursor = db.cursor()
    query = "INSERT INTO productos (nombre, precio, cantidad) VALUES (%s, %s, %s)"
    cursor.execute(query, (nombre, precio, cantidad))
    db.commit()
    cursor.close()
    db.close()
    return RedirectResponse(url="/inventario", status_code=303)

# Página para mostrar el inventario
@app.get("/inventario", response_class=HTMLResponse)
async def ver_inventario(request: Request):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    inventario = cursor.fetchall()
    cursor.close()
    db.close()
    return templates.TemplateResponse("inventario.html", {"request": request, "inventario": inventario})

# Página para simular una venta
@app.get("/venta", response_class=HTMLResponse)
async def venta(request: Request):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    inventario = cursor.fetchall()
    cursor.close()
    db.close()
    return templates.TemplateResponse("venta.html", {"request": request, "inventario": inventario})

# Endpoint para registrar una venta
@app.post("/registrar-venta")
async def registrar_venta(producto_id: int = Form(...), cantidad_vendida: int = Form(...)):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Verificar si hay suficiente stock
    cursor.execute("SELECT cantidad FROM productos WHERE id = %s", (producto_id,))
    producto = cursor.fetchone()
    if producto["cantidad"] < cantidad_vendida:
        raise HTTPException(status_code=400, detail="No hay suficiente stock")

    # Actualizar el inventario
    nueva_cantidad = producto["cantidad"] - cantidad_vendida
    cursor.execute("UPDATE productos SET cantidad = %s WHERE id = %s", (nueva_cantidad, producto_id))

    # Registrar la venta
    cursor.execute("INSERT INTO ventas (producto_id, cantidad_vendida) VALUES (%s, %s)", (producto_id, cantidad_vendida))
    db.commit()
    cursor.close()
    db.close()
    return RedirectResponse(url="/inventario", status_code=303)