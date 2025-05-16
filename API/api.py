from flask import Flask, jsonify, request
from flask_cors import CORS  # Importa CORS
from unofficial_livecounts_api.twitter import TwitterAgent
from datetime import datetime
import pytz  # Importar pytz para manejar zonas horarias

app = Flask(__name__)

# Habilitar CORS para todas las rutas
CORS(app)

# Variable global para almacenar el nombre de usuario
nombre_usuario = "elonmusk"  # Valor inicial

# Zona horaria de Lima (UTC-5)
LIMA_TZ = pytz.timezone('America/Lima')

@app.route('/')
def index():
    return "¡Bienvenido a la API de monitoreo de seguidores de Twitter!"

# Endpoint para obtener el nombre de usuario actual
@app.route('/nombre_usuario', methods=['GET'])
def obtener_nombre_usuario():
    return jsonify({"nombre_usuario": nombre_usuario}), 200

# Endpoint para actualizar el nombre de usuario
@app.route('/nombre_usuario', methods=['POST'])
def actualizar_nombre_usuario():
    global nombre_usuario
    # Obtener el nuevo nombre de usuario desde los datos JSON de la solicitud
    data = request.get_json()
    
    # Verificar si el 'nombre_usuario' está en los datos
    if 'nombre_usuario' not in data:
        return jsonify({"error": "El campo 'nombre_usuario' es obligatorio"}), 400

    nombre_usuario = data['nombre_usuario']
    return jsonify({"nombre_usuario": nombre_usuario}), 200

# Endpoint para monitorear los seguidores del usuario actual
@app.route('/monitoreo/nombre_usuario', methods=['GET'])
def monitorear_seguidores_usuario():
    global nombre_usuario

    try:
        # Obtener las métricas del usuario de Twitter actual
        metricas = TwitterAgent.fetch_user_metrics(query=nombre_usuario)

        # Extraer las métricas relevantes
        seguidores = metricas.follower_count
        tweets = metricas.tweet_count
        following = metricas.following_count

        # Obtener la hora actual en la zona horaria de Lima (UTC-5)
        hora_lima = datetime.now(LIMA_TZ).strftime('%d-%m-%Y %H:%M:%S')

        # Crear la respuesta en formato JSON
        respuesta = {
            "hora": hora_lima,
            "usuario": f"@{nombre_usuario}",
            "seguidores": seguidores,
            "tweets": tweets,
            "following": following
        }

        # Imprimir el resultado
        print(f"[{respuesta['hora']}] @{nombre_usuario} | Seguidores: {seguidores} | Tweets: {tweets} | Following: {following}")

        return jsonify(respuesta), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)