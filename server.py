from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib import parse
import json

# Importa desde la raíz del proyecto (mismos nivel que server.py)
import crud_alumno
import crud_docente

port = 3000

crudAlumno = crud_alumno.crud_alumno()
crudDocente = crud_docente.crud_docente()


class miServidor(SimpleHTTPRequestHandler):
    # Utilidad para responder JSON
    def send_json(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    # (Opcional) CORS preflight
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        # Soporta query ?buscar=...
        path, _, query = self.path.partition("?")
        params = parse.parse_qs(query)
        buscar = params.get("buscar", [""])[0]

        if path == "/":
            self.path = "index.html"
            return SimpleHTTPRequestHandler.do_GET(self)

        if path == "/alumnos":
            alumnos = crudAlumno.consultar(buscar)
            return self.send_json(200, alumnos)

        if path == "/docentes":
            docentes = crudDocente.consultar(buscar)
            return self.send_json(200, docentes)

        # Cualquier otro recurso estático
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        # Lee body (JSON)
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"

        try:
            datos = json.loads(raw)
        except json.JSONDecodeError:
            datos = json.loads(parse.unquote(raw))

        # Ruteo por path
        if self.path == "/alumnos":
            res = {"msg": crudAlumno.administrar(datos)}
            return self.send_json(200, res)

        if self.path == "/docentes":
            res = {"msg": crudDocente.administrar(datos)}
            return self.send_json(200, res)

        return self.send_json(404, {"msg": "ruta no encontrada"})


print("Servidor ejecutándose en el puerto", port)
server = HTTPServer(("localhost", port), miServidor)
server.serve_forever()
