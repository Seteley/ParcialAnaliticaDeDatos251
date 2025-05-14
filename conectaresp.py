import requests

# Dirección IP del ESP32 (cambia esta dirección por la IP de tu ESP32)
esp32_ip = "http://192.168.1.100/set_usuario"  # IP del ESP32
usuario = input("Introduce el nombre de usuario de Twitter: ")

# Realizar una solicitud POST al ESP32 para cambiar el nombre de usuario
payload = {'usuario': usuario}  # El nombre de usuario que se va a enviar
response = requests.post(esp32_ip, data=payload)

# Comprobar la respuesta del ESP32
if response.status_code == 200:
    print(f"Nombre de usuario actualizado a: {usuario}")
else:
    print(f"Error al actualizar el nombre de usuario. Código de error: {response.status_code}")
