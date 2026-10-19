import requests
import json
from datetime import datetime, date, timedelta
from faker import Faker
import random

BASE_URL = "http://localhost:8080"

# Inicializo faker en español 
fake = Faker('es_ES')

def test_crear_estudiante()-> int:
    """Implementar test para crear una tarea"""
    print("===================== TEST 1: CREAR ESTUDIANTE =====================")
    nombre=fake.name()
    estudiante={
        "nombre": nombre,
        "email": nombre.replace(" ","") + "@gmail.com",
        "edad": random.randint(15,80)
     }
    response= requests.post(BASE_URL + "/estudiantes",json=estudiante)
    print(f"Código de respuesta:{response.status_code}")
    print(f"Respuesta:{response.json()}")
    return response.json()["id"]
    pass

def test_obtener_estudiante(estudiante_id:int):
    """Implementación test para obtener un estudiante por ID"""
    print("===================== TEST 2: OBTENER ESTUDIANTE =====================")
    response= requests.get(BASE_URL + f"/estudiantes/{estudiante_id}")
    print(f"Codigo de respuesta:{response.status_code}")
    print(f"Respuesta: {response.json()}")
    pass

def test_listar_estudiantes():
    """Implementación test para listar estudiantes"""
    print("===================== TEST 3: LISTAR ESTUDIANTES =====================")
    response = requests.get(BASE_URL + "/estudiantes")
    print(f"Código de respuesta:{response.status_code}")
    print(f"Respuesta:{response.json()}")
    pass

def test_eliminar_estudiante(estudiante_id:int):
    """ Implementación test para eliminar un estudiante """
    print("===================== TEST 4: ELIMINAR ESTUDIANTE =====================")
    response= requests.delete(BASE_URL + f"/estudiantes/{estudiante_id}")
    print(f"Código de respuesta:{response.status_code}")
    print(f"Estudiante con id:{estudiante_id} eliminado!")
            
    pass

def test_datos_incorrectos():
    """Implementar test con datos incorrectos que debe devolver 400"""
    print("===================== TEST 5: VALIDAR DATOS INCORRECTOS ESTUDIANTE =====================")
    # Escenarios de prueba
    escenarios_prueba=[
        {"nombre": "","email":"prueb@r.co", "edad":15},
        {"nombre": "Susan Lopez","email":"", "edad":23},
         {"nombre": "Susan Lopez5","email":"susilo@gmail.com", "edad":23},
        {"email":"email@io.es", "edad": 25},
        {"nombre": "Fatima Li Lau","email":"guty@gt.es", "edad": -33}
   ]    
    i=0
    for escenario in escenarios_prueba:
        i+=1
        response = requests.post(BASE_URL + "/estudiantes",json=escenario)
        print(f"Caso prueba {i}: Código de respuesta: {response.status_code}")
        if response.status_code!=422:
            raise Exception(f"Caso prueba {i}, ha fallado, esperaba 422 y se obtuvo {response.status_code}")
    print("Todos los casos de prueba se han validado correctamente, y retornan 422")
    pass

if __name__ == "__main__":
    print("____________________________ Ejecutando tests ____________________________")
    # Llamadas a las funciones de test y validar resultados
    estudiante_id=test_crear_estudiante()
    test_obtener_estudiante(estudiante_id)
    test_listar_estudiantes()
    test_eliminar_estudiante(estudiante_id)
    test_datos_incorrectos()
    print("____________________________ Tests completados ____________________________")
