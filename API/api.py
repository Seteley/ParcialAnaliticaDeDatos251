from flask import Flask, jsonify, request
from flask_cors import CORS  # Importa CORS
from unofficial_livecounts_api.twitter import TwitterAgent
from datetime import datetime

app = Flask(__name__)

# Habilitar CORS para todas las rutas
CORS(app)

@app.route('/')
def index():
    return "¡Bienvenido a la API de monitoreo de seguidores de Twitter!"


# Endpoint para monitorear los seguidores de un usuario dinámico
@app.route('/<nombre_usuario>', methods=['GET'])
def monitorear_seguidores_usuario(nombre_usuario):
    try:
        # Obtener las métricas del usuario de Twitter usando el nombre de usuario dinámico
        metricas = TwitterAgent.fetch_user_metrics(query=nombre_usuario)

        # Extraer las métricas relevantes
        seguidores = metricas.follower_count
        tweets = metricas.tweet_count
        following = metricas.following_count

        # Crear la respuesta en formato JSON
        respuesta = {
            "hora": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
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