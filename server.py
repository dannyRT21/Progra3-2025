from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import crud_alumno
import crud_docente
import crud_materias
import crud_notas  # <-- NOTAS: import

port = 5000

crudAlumno = crud_alumno.crud_alumno()
crudDocente = crud_docente.crud_docente()
crudMateria = crud_materias.crud_materia()
crudNota   = crud_notas.crud_notas()  # <-- NOTAS: instancia


class miServidor(SimpleHTTPRequestHandler):

    def do_GET(self):
        url_parseada = urlparse(self.path)
        path = url_parseada.path
        parametros = parse_qs(url_parseada.query)

        if self.path == "/":
            self.path = "index.html"
            return SimpleHTTPRequestHandler.do_GET(self)

        # ---------- ALUMNOS ----------
        if path == "/alumnos":
            buscar = parametros.get('buscar', [""])[0]
            try:
                alumnos = crudAlumno.consultar(buscar)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(alumnos, default=str).encode("utf-8"))
            except Exception as ex:
                print("ERROR /alumnos:", ex)
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"msg": f"error: {str(ex)}"}, default=str).encode("utf-8"))
            return

        # ---------- DOCENTES ----------
        if path == "/docentes":
            buscar = parametros.get('buscar', [""])[0]
            try:
                docentes = crudDocente.consultar(buscar)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(docentes, default=str).encode("utf-8"))
            except Exception as ex:
                print("ERROR /docentes:", ex)
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"msg": f"error: {str(ex)}"}, default=str).encode("utf-8"))
            return

        # ---------- MATERIAS ----------
        if path == "/materias":
            buscar = parametros.get('buscar', [""])[0]
            try:
                materias = crudMateria.consultar(buscar) or []
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(materias, default=str).encode("utf-8"))
            except Exception as ex:
                print("ERROR /materias:", ex)
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"msg": f"error: {str(ex)}"}, default=str).encode("utf-8"))
            return

        # ---------- NOTAS ----------  <-- NOTAS: GET
        if path == "/notas":
            buscar = parametros.get('buscar', [""])[0]
            try:
                notas = crudNota.consultar(buscar) or []
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(notas, default=str).encode("utf-8"))
            except Exception as ex:
                print("ERROR /notas:", ex)
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"msg": f"error: {str(ex)}"}, default=str).encode("utf-8"))
            return

        # ---------- VISTAS PARCIALES ----------
        if path == "/vistas":
            # Sirve vistas parciales desde /modulos?form=nombre
            form = parametros.get('form', [None])[0]
            if not form:
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(b'{"msg":"Parametro form requerido"}')
                return

            # pequeña sanitización para evitar ../
            seguro = "".join(ch for ch in form if ch.isalnum() or ch in ("_", "-"))
            if not seguro:
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(b'{"msg":"Nombre de vista invalido"}')
                return

            self.path = '/modulos/' + seguro + '.html'
            return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        # Leer body
        try:
            longitud = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            longitud = 0

        body = self.rfile.read(longitud).decode("utf-8")

        # Parsear JSON
        try:
            datos = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(b'{"msg":"JSON invalido"}')
            return

        # Enrutamiento por PATH
        if self.path == "/alumnos":
            target = crudAlumno
        elif self.path == "/docentes":
            target = crudDocente
        elif self.path == "/materias":
            target = crudMateria
        elif self.path == "/notas":              # <-- NOTAS: POST directo
            target = crudNota
        else:
            # Fallback por 'tabla' en el JSON (opcional)
            tabla = (datos.get('tabla') or '').lower()
            if tabla in ('docentes', 'docente'):
                target = crudDocente
            elif tabla in ('alumnos', 'alumno'):
                target = crudAlumno
            elif tabla in ('materias', 'materia'):
                target = crudMateria
            elif tabla in ('notas', 'nota'):      # <-- NOTAS: fallback
                target = crudNota
            else:
                self.send_response(404)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(b'{"msg":"Ruta o tabla no soportada"}')
                return

        # Ejecutar la operación en el CRUD correspondiente
        try:
            resultado = target.administrar(datos)
            # Se espera que db.ejecutar retorne "ok" al terminar satisfactoriamente
            resp = {"msg": resultado}
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        except Exception as ex:
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"msg": f"error: {str(ex)}"}).encode("utf-8"))


print("Servidor ejecutandose en el puerto", port)
server = HTTPServer(("localhost", port), miServidor)
server.serve_forever()
