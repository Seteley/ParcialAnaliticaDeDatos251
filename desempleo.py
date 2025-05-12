import requests
from bs4 import BeautifulSoup
import pandas as pd

# Lista de indicadores esperados
indicadores_esperados = [
    "Ganancias horarias promedio (Mensual)",
    "Ganancias promedio por hora (Interanual)",
    "Promedio de horas semanales",
    "Personas ocupadas",
    "Índice De Costo De Empleo",
    "Employment Cost - Benefits",
    "Employment Cost - Wages",
    "Tasa De Empleo",
    "Trabajadores a tiempo completo",
    "Nóminas gubernamentales",
    "Despidos laborales y despidos",
    "Jolts Vacantes de Empleo",
    "Renuncias laborales informe JOLTs",
    "Tasa de abandonos del trabajo",
    "Ofertas de empleo",
    "Tasa de participación",
    "Salarios",
    "Tasa de desempleo de largo plazo",
    "Nóminas manufactureras",
    "Nóminas no agrícolas",
    "Nóminas privadas no agrícolas",
    "Productividad No Agrícola",
    "Empleo de Tiempo Parcial",
    "Productividad",
    "Tasa de desempleo U-6",
    "Personas desempleadas",
    "Tasa de desempleo",
    "Costes laborales unitarios",
    "Salarios",
    "Salarios en la industria",
    "Tasa de desempleo juvenil"
]

# URL del sitio
url = 'https://es.tradingeconomics.com/united-states/u6-unemployment-rate'

headers = {
    'User-Agent': 'Mozilla/5.0',
    'Accept-Language': 'es-ES,es;q=0.9'
}

# Realizar la solicitud
response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    # Buscar el div que contiene la tabla de indicadores relacionados
    tabla_div = soup.select_one('#ctl00_ContentPlaceHolder1_ctl00_ctl02_PanelPeers table')

    if tabla_div:
        filas = tabla_div.find_all('tr')

        # Lista para almacenar los valores encontrados
        fila_datos = []

        # Iterar sobre las filas de la tabla
        for i, fila in enumerate(filas):
            columnas = fila.find_all('td')
            
            if len(columnas) >= 2:
                # Extraer el valor del primer td (solo el valor)
                valor = columnas[1].get_text(strip=True).replace(",", "")
                fila_datos.append(valor)

        # Completar la lista de datos con None si hay valores faltantes
        while len(fila_datos) < len(indicadores_esperados):
            fila_datos.append(None)

        # Crear DataFrame y guardar como CSV
        df = pd.DataFrame([fila_datos], columns=indicadores_esperados)
        df.to_csv('indicadores_relacionados.csv', index=False)

        print("✅ CSV guardado como 'indicadores_relacionados.csv'")
    else:
        print("❌ No se encontró el contenedor de la tabla de indicadores.")
else:
    print(f"❌ Error {response.status_code} al acceder a la página.")
