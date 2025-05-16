import requests
import serial
import json
import os
from datetime import datetime

def actualizar_nombre_usuario_api(usuario):
    # URL de tu API Flask (ajústala si estás usando un dominio o IP distinta)
    url = 'https://parcialanaliticadedatos251-1.onrender.com/nombre_usuario'  # Usa la IP de tu servidor si no es local

    # Datos que se enviarán en formato JSON
    datos = {
        "nombre_usuario": usuario
    }

    try:
        # Realizar la solicitud POST con los datos JSON
        response = requests.post(url, json=datos)

        # Verificar si fue exitosa
        if response.status_code == 200:
            pass  # Aquí no se imprime nada si es exitoso
        else:
            pass  # Aquí no se imprime nada si hay error en la respuesta
    except Exception as e:
        pass  # No imprimir nada en caso de error

def guardar_datos_en_json(datos, nombre_archivo="datos.json"):
    # Asegurar que la carpeta 'datos_json' exista
    if not os.path.exists("datos_json"):
        os.makedirs("datos_json")

    ruta = os.path.join("datos_json", nombre_archivo)

    # Leer los datos anteriores si existen
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
        # Crear el archivo con el primer dato
        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump([datos], archivo, indent=2, ensure_ascii=False)

def consultar_serial(puerto="COM4", baudrate=115200, timeout=5, nombre_archivo="datos.json"):
    try:
        with serial.Serial(puerto, baudrate, timeout=timeout) as ser:
            buffer_json = ""
            leyendo_json = False

            while True:
                linea = ser.readline().decode('utf-8', errors='ignore').strip()
                if not linea:
                    continue

                if "{" in linea:
                    buffer_json = ""
                    leyendo_json = True

                if leyendo_json:
                    buffer_json += linea
                    if "}" in linea:
                        leyendo_json = False
                        try:
                            data = json.loads(buffer_json)
                            guardar_datos_en_json(data, nombre_archivo)
                        except json.JSONDecodeError as e:
                            buffer_json = ""
    except serial.SerialException as e:
        pass  # No imprimir nada en caso de error al abrir el puerto serial

# Llamada a la función, ahora puedes pasar el nombre del archivo JSON
nombre_archivo = "seguidores_elonmusk.json"  # Puedes cambiar este nombre
consultar_serial(nombre_archivo=nombre_archivo)