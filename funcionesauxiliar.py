import requests

def obtener_link_dashboard():
    """
    Obtiene el enlace público actual de ngrok desde el dashboard local.

    Returns:
        str: URL pública de ngrok (por ejemplo: https://xxxxx.ngrok-free.app)
    Raises:
        Exception: Si no se puede acceder al dashboard o no se encuentra ningún túnel.
    """
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels")
        response.raise_for_status()
        data = response.json()
        tunnels = data.get("tunnels", [])

        if not tunnels:
            raise Exception("No hay túneles activos en ngrok.")

        # Obtener el primer túnel con campo public_url
        for tunnel in tunnels:
            public_url = tunnel.get("public_url")
            if public_url:
                return public_url

        raise Exception("No se encontró una URL pública en los túneles activos.")

    except requests.RequestException as e:
        raise Exception(f"Error al conectarse con el dashboard de ngrok: {e}")