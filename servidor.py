from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib import parse
import json
import os
import sys

# Puerto y cambio de carpeta para servir archivos
PORT = 2020
os.chdir(os.path.join(os.path.dirname(__file__), "Templates"))

# Agregar carpeta Model al path
sys.path.append(os.path.join(os.path.dirname(__file__), "Model"))

# Importar el CRUD
from crud_comentarios import CrudComentarios
crudComentarios = CrudComentarios()

class ServidorArchivos(SimpleHTTPRequestHandler):
    def send_json(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path, _, query = self.path.partition("?")
        params = parse.parse_qs(query)
        buscar = params.get("buscar", [""])[0]

        if path == "/comentarios":
            resultado = crudComentarios.consultar(buscar)
            return self.send_json(200, resultado)

        return super().do_GET()

def do_POST(self):
    print("🔔 do_POST llamada, path:", self.path)
    length = int(self.headers.get("Content-Length", 0))
    raw = self.rfile.read(length).decode("utf-8") if length else "{}"
    print("Raw body:", raw)

    try:
        datos = json.loads(raw)
    except json.JSONDecodeError as e:
        print("Error JSON:", e)
        datos = {}

    if self.path == "/comentarios":
        print("📥 Comentario recibido:", datos)
        resultado = crudComentarios.administrar(datos)
        print("Resultado crud:", resultado)
        return self.send_json(200, {"msg": resultado})

    print("Ruta no encontrada en POST:", self.path)
    return self.send_json(404, {"msg": "Ruta no encontrada"})


def run():
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, ServidorArchivos)
    print(f"🚀 Servidor corriendo en http://localhost:{PORT}")

    httpd.serve_forever()

if __name__ == "__main__":
    run()
