from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib import parse
from urllib.parse import urlparse, parse_qs
import os
import json
import numpy as np

# Configuración de logs de TensorFlow
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf

# Cargar el modelo existente (C -> F)
model = tf.keras.models.load_model('grados.h5')
port = 3000

class miServidor(SimpleHTTPRequestHandler):
    def do_GET(self):
        url_parseada = urlparse(self.path)
        
        if self.path == "/":
            self.path = "index.html"
            return SimpleHTTPRequestHandler.do_GET(self)
        
        # Permite servir otros archivos estáticos (css, js, etc)
        return SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        # 1. Obtener longitud y leer datos
        longitud = int(self.headers['Content-Length'])
        datos = self.rfile.read(longitud)
        datos = datos.decode("utf-8")
        datos = parse.unquote(datos) # No es estrictamente necesario con JSON puro, pero se deja por compatibilidad
        datos = json.loads(datos)
        
        resp = {}

        # 2. Rutas (Endpoints)
        
        # CASO 1: Celsius a Fahrenheit (Usando el Modelo IA)
        if self.path == "/celsiusToFahrenheit":
            c = float(datos['celsius']) # Usar float es más seguro que int
            prediccion = model.predict(np.array([c]), verbose=0)
            resp = {"grados": str(prediccion[0][0])}

        # CASO 2: Fahrenheit a Celsius (Usando Fórmula Matemática)
        elif self.path == "/fahrenheitToCelsius":
            f = float(datos['fahrenheit'])
            # Fórmula: (F - 32) * 5/9
            c_calculado = (f - 32) * 5.0 / 9.0
            resp = {"grados": str(c_calculado)}
        
        else:
            # Ruta no encontrada
            resp = {"error": "Ruta no válida"}

        # 3. Enviar respuesta
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*") # Opcional: Para evitar problemas de CORS si abres el HTML directo
        self.end_headers()
        self.wfile.write(json.dumps(resp).encode("utf-8"))

print("Servidor ejecutandose en el puerto", port)
server = HTTPServer(("localhost", port), miServidor)
server.serve_forever()