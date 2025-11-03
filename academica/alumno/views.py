from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

# Create your views here.
def holaMundo(request):
    return HttpResponse(request, 'Hola Mundo')

def miEdad(request, edad):
    return HttpResponse(f'Tengo {edad} años, que feliz')
def saludoNombre(request, nombre):
    return HttpResponse(f'Hola, {nombre}, bienvenida a nuestra plataforma académica .')

def index(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render())
  