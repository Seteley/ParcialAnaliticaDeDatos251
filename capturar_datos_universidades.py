import requests
import json
import os
from datetime import datetime
import time

# Lista de universidades y sus respectivos nombres de usuario en X
universidades = {
    "UNI": "UNIoficial",
    "UNMSM": "UNMSM_",
    "UNFV": "UNFVoficial",
    "PUCP": "pucp"
}

# URL base de la API desplegada en Render
BASE_URL = "https://parcialanaliticadedatos251-1.onrender.com"

# Función para cambiar el nombre de usuario en la API
def cambiar_nombre_usuario(nombre_usuario):
    try:
        url = f'{BASE_URL}/nombre_usuario'
        response = requests.post(url, json={"nombre_usuario": nombre_usuario})
        
        if response.status_code == 200:
            return response.json()  # Devuelve la respuesta confirmando el cambio
        else:
            return {"error": f"Error al cambiar nombre de usuario para {nombre_usuario}, status code {response.status_code}"}
    except Exception as e:
        return {"error": f"Error al cambiar nombre de usuario: {str(e)}"}

# Función para obtener los datos de seguidores y tweets
def obtener_datos_universidad(nombre_usuario):
    try:
        url = f'{BASE_URL}/monitoreo/nombre_usuario'
        response = requests.get(url, params={"nombre_usuario": nombre_usuario})
        
        if response.status_code == 200:
            return response.json()  # Devuelve los datos del monitoreo
        else:
            return {"error": f"No se pudo obtener los datos de {nombre_usuario}, status code {response.status_code}"}
    except Exception as e:
        return {"error": f"Error al consultar datos: {str(e)}"}

# Función para guardar los datos en un archivo JSON
def guardar_datos_en_json(datos, nombre_archivo):
    if not os.path.exists("datos_json"):
        os.makedirs("datos_json")

    ruta = os.path.join("datos_json", nombre_archivo)

    if os.path.exists(ruta):
        with open(ruta, "r+", encoding="utf-8") as archivo:
            try:
                datos_guardados = json.load(archivo)
                if not isinstance(datos_guardados, list):
                    datos_guardados = [datos_guardados]
            except json.JSONDecodeError:
                datos_guardados = []
            datos_guardados.append(datos)
            archivo.seek(0)
            json.dump(datos_guardados, archivo, indent=2, ensure_ascii=False)
    else:
        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump([datos], archivo, indent=2, ensure_ascii=False)

# Función principal para capturar y almacenar los datos de cada universidad en tiempo real
def capturar_datos_universidades_en_tiempo_real():
    while True:  # Bucle infinito para seguir capturando datos
        for universidad, usuario in universidades.items():
            print(f"Obteniendo datos de {universidad} ({usuario})...")

            # Paso 1: Cambiar el nombre de usuario
            print(f"Cambiando nombre de usuario a {usuario}...")
            cambio_usuario = cambiar_nombre_usuario(usuario)
            
            if "error" in cambio_usuario:
                print(cambio_usuario["error"])
                continue  # Si hubo un error, continuar con la siguiente universidad

            # Paso 2: Obtener los datos de esa universidad
            print(f"Obteniendo datos de {usuario}...")
            datos = obtener_datos_universidad(usuario)

            if "error" not in datos:
                # Si los datos son válidos, almacenar los datos en un archivo JSON
                hora_actual = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                registro = {
                    "following": datos['following'],
                    "hora": hora_actual,
                    "seguidores": datos['seguidores'],
                    "tweets": datos['tweets'],
                    "usuario": f"@{usuario}"
                }
                guardar_datos_en_json(registro, f"seguidores_{universidad}.json")
            else:
                print(datos["error"])

        # Esperar 5 segundos antes de obtener los nuevos datos
        print("Esperando 5 segundos para la siguiente captura...")
        time.sleep(5)  # Esperar 5 segundos antes de hacer la siguiente consulta

# Ejecutar la función para capturar los datos en tiempo real
capturar_datos_universidades_en_tiempo_real()