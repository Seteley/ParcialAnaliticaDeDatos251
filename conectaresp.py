import serial
import time

# Configurar el puerto serial para enviar el nombre de usuario al ESP32
# Asegúrate de usar el puerto correcto (por ejemplo, COM3 en Windows o /dev/ttyUSB0 en Linux/Mac)
ser = serial.Serial('/dev/ttyUSB0', 115200)  # Ajusta el puerto y la velocidad de baudios si es necesario

# Nombre de usuario que deseas enviar
nombre_usuario = "@elonmusk"

# Espera unos segundos para asegurar que el ESP32 se haya inicializado
time.sleep(2)

# Enviar el nombre de usuario al ESP32
ser.write(nombre_usuario.encode())  # Convertir el string a bytes y enviarlo

# Cerrar la comunicación serial
ser.close()