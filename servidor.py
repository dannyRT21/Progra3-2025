from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

# Cambia el directorio de trabajo a la carpeta Templates (donde están los HTML y recursos)
os.chdir(os.path.join(os.path.dirname(__file__), "Templates"))

class ServidorArchivos(SimpleHTTPRequestHandler):
    pass  # Puedes agregar cabeceras CORS u otras personalizaciones si lo necesitas

def run(server_class=HTTPServer, handler_class=ServidorArchivos, port=2020):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Servidor corriendo en http://localhost:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
