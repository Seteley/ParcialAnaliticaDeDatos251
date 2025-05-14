import serial
import time

# Función para enviar el nombre de usuario al ESP32
def enviar_nombre_usuario(nombre_usuario, puerto_com='COM4', velocidad_baudios=115200):
    try:
        # Conectar al puerto serial del ESP32
        ser = serial.Serial(puerto_com, velocidad_baudios)
        print(f"Conectado al puerto {puerto_com} a {velocidad_baudios} baudios")

        # Espera unos segundos para asegurar que el ESP32 se haya inicializado
        time.sleep(2)

        # Enviar el nombre de usuario al ESP32
        ser.write(nombre_usuario.encode())  # Convertir el string a bytes y enviarlo
        print(f"Nombre de usuario '{nombre_usuario}' enviado al ESP32.")

        # Cerrar la comunicación serial
        ser.close()
        print("Comunicación serial cerrada.")
    
    except serial.SerialException as e:
        print(f"Error al intentar conectar con el puerto {puerto_com}: {e}")

# Llamar a la función con el nombre de usuario que deseas enviar
nombre_usuario = "@elonmusk"
enviar_nombre_usuario(nombre_usuario)

# Después de un tiempo, puedes cambiar el nombre de usuario dinámicamente:
time.sleep(5)  # Espera 5 segundos
nombre_usuario = "@cristiano"
enviar_nombre_usuario(nombre_usuario)