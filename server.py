from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import crud_alumno
import crud_docente

port = 5000

crudAlumno = crud_alumno.crud_alumno()
crudDocente = crud_docente.crud_docente()

class miServidor(SimpleHTTPRequestHandler):

    def do_GET(self):
        url_parseada = urlparse(self.path)
        path = url_parseada.path
        parametros = parse_qs(url_parseada.query)

        if self.path == "/":
            self.path = "index.html"
            return SimpleHTTPRequestHandler.do_GET(self)

        if self.path == "/alumnos":
            alumnos = crudAlumno.consultar("")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(alumnos).encode("utf-8"))
            return

        if self.path == "/docentes":
            docentes = crudDocente.consultar("")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(docentes).encode("utf-8"))
            return

        if path == "/vistas":
            # sirve vistas parciales desde /modulos?form=nombre
            self.path = '/modulos/' + parametros['form'][0] + '.html'
            return SimpleHTTPRequestHandler.do_GET(self)

        # fallback: servir archivos estáticos (js, css, modulos/*, etc.)
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        # Leer body
        try:
            longitud = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            longitud = 0

        body = self.rfile.read(longitud).decode("utf-8")

        # Parsear JSON (sin unquote)
        try:
            datos = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(b'{"msg":"JSON invalido"}')
            return

        # Enrutamiento por PATH (recomendado)
        if self.path == "/alumnos":
            target = crudAlumno
        elif self.path == "/docentes":
            target = crudDocente
        else:
            # Fallback por 'tabla' en el JSON (opcional)
            tabla = (datos.get('tabla') or '').lower()
            if tabla in ('docentes', 'docente'):
                target = crudDocente
            elif tabla in ('alumnos', 'alumno'):
                target = crudAlumno
            else:
                self.send_response(404)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(b'{"msg":"Ruta o tabla no soportada"}')
                return

        # Ejecutar la operación en el CRUD correspondiente
        try:
            resultado = target.administrar(datos)
            resp = {"msg": resultado}
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        except Exception as ex:
            # Manejo de errores en CRUD
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"msg": f"error: {str(ex)}"}).encode("utf-8"))

print("Servidor ejecutandose en el puerto", port)
server = HTTPServer(("localhost", port), miServidor)
server.serve_forever()
