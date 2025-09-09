from http.server import HTTPServer, SimpleHTTPRequestHandler
port = 3000
class Myserver(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
            return SimpleHTTPRequestHandler.do_GET(self)
        
print ("Arranco el server ",port)  
server = HTTPServer(('localhost', port), Myserver)
server.serve_forever()




