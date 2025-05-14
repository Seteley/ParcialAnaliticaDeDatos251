import requests

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
            print("✅ Nombre de usuario actualizado correctamente:")
            print(response.json())
        else:
            print(f"❌ Error al actualizar: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ Error de conexión: {e}")

# Ejemplo de uso
usuario = "elonmusk"
actualizar_nombre_usuario_api(usuario)
