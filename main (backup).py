from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Montar la carpeta "static" para archivos CSS/JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar Jinja2 para las plantillas HTML
templates = Jinja2Templates(directory="templates")

# Base de datos "ficticia" (en un caso real usarías una base de datos como SQLite)
inventario = []
ventas = []

# Página principal (registrar productos)
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Endpoint para agregar un producto
@app.post("/agregar-producto")
async def agregar_producto(nombre: str = Form(...), precio: float = Form(...), cantidad: int = Form(...)):
    producto = {"nombre": nombre, "precio": precio, "cantidad": cantidad}
    inventario.append(producto)
    return RedirectResponse(url="/inventario", status_code=303)

# Página para mostrar el inventario
@app.get("/inventario", response_class=HTMLResponse)
async def ver_inventario(request: Request):
    return templates.TemplateResponse("inventario.html", {"request": request, "inventario": inventario})

# Página para simular una venta
@app.get("/venta", response_class=HTMLResponse)
async def venta(request: Request):
    return templates.TemplateResponse("venta.html", {"request": request, "inventario": inventario})

# Endpoint para registrar una venta
@app.post("/registrar-venta")
async def registrar_venta(producto_id: int = Form(...), cantidad_vendida: int = Form(...)):
    producto = inventario[producto_id]
    if producto["cantidad"] >= cantidad_vendida:
        producto["cantidad"] -= cantidad_vendida
        ventas.append({"producto": producto["nombre"], "cantidad_vendida": cantidad_vendida})
        return RedirectResponse(url="/inventario", status_code=303)
    else:
        return {"error": "No hay suficiente stock"}