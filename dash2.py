from dash import Dash, html, dcc, Input, Output
import json
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timezone

# Lista de universidades y sus respectivos nombres de usuario en X
universidades = {
    "UNI": "UNIoficial",
    "UNMSM": "UNMSM_",
    "UNFV": "UNFVoficial",
    "PUCP": "pucp"
}

# Función para obtener el rango de tiempo (mínimo y máximo) de los datos de cada universidad
def obtener_rango_tiempo(universidad):
    archivo_json = f'datos_json/seguidores_{universidad}.json'
    with open(archivo_json, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    df = pd.DataFrame(datos)
    df['hora'] = pd.to_datetime(df['hora'], format='%d-%m-%Y %H:%M:%S')  # Convertir la columna 'hora' a datetime
    min_hora = df['hora'].min()  # Fecha y hora mínima
    max_hora = df['hora'].max()  # Fecha y hora máxima
    return min_hora, max_hora

# Función para filtrar los datos según el rango de tiempo seleccionado
def filtrar_datos_por_rango(df, rango):
    # Convertir los valores del rango (timestamp) a datetime (timezone-aware)
    min_timestamp = datetime.fromtimestamp(rango[0], tz=timezone.utc)
    max_timestamp = datetime.fromtimestamp(rango[1], tz=timezone.utc)
    
    # Asegurarse de que la columna 'hora' también esté en formato timezone-aware UTC
    df['hora'] = pd.to_datetime(df['hora']).dt.tz_localize('UTC')

    # Filtrar los datos según el rango de tiempo
    df_filtrado = df[(df['hora'] >= min_timestamp) & (df['hora'] <= max_timestamp)]
    return df_filtrado

# Función para crear el gráfico comparativo de seguidores
def crear_grafico_comparativo(df_rango_universidades, universidades, metric, ajustado=False):
    fig = go.Figure()

    # Colores distintivos para cada universidad
    colores = {
        'UNI': '#1E90FF',  # Azul para UNI
        'UNMSM': '#FF6347',  # Rojo para UNMSM
        'UNFV': '#32CD32',  # Verde para UNFV
        'PUCP': '#FFD700'  # Amarillo para PUCP
    }

    for universidad in universidades:
        df = df_rango_universidades[universidad]
        fig.add_trace(go.Scatter(
            x=df['hora'],
            y=df[metric],
            mode='lines+markers',
            line=dict(color=colores[universidad]),
            name=f"{metric.capitalize()} - {universidad}",
        ))

    # Ajustar el rango del eje Y solo cuando se seleccione una universidad
    if ajustado:
        max_value = df[metric].max() + (df[metric].max() * 0.1)  # Agregar un 10% más al valor máximo
        min_value = df[metric].min() - (df[metric].min() * 0.1)  # Reducir un 10% al valor mínimo
    else:
        max_value = max([df[metric].max() for df in df_rango_universidades.values()]) + (0.1 * max([df[metric].max() for df in df_rango_universidades.values()]))
        min_value = min([df[metric].min() for df in df_rango_universidades.values()]) - (0.1 * min([df[metric].min() for df in df_rango_universidades.values()]))

    fig.update_layout(
        title=f'Comparativo de {metric.capitalize()} en Twitter entre Universidades',
        xaxis_title='Hora',
        yaxis_title=f'Número de {metric.capitalize()}',
        template='plotly_dark',  # Usamos un tema oscuro para que los colores resalten
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',  # Fondo negro para los gráficos
        paper_bgcolor='#2F2F2F',  # Fondo general oscuro
        font=dict(color='white'),
        margin=dict(t=40, b=40, l=60, r=40),
        yaxis=dict(
            range=[min_value, max_value],  # Establecer el rango del eje Y
        )
    )

    return fig

# Función para crear el resumen comparativo de todas las universidades
def crear_resumen_comparativo(df_rango_universidades, universidades):
    resumenes = []
    for universidad in universidades:
        df = df_rango_universidades[universidad]
        
        # Últimos valores de seguidores y tweets
        seguidores_actual = df['seguidores'].iloc[-1]
        seguidores_inicial = df['seguidores'].iloc[0]
        tweets_actual = df['tweets'].iloc[-1]
        tweets_inicial = df['tweets'].iloc[0]

        # Cálculo de variaciones
        variacion_seguidores = seguidores_actual - seguidores_inicial
        variacion_tweets = tweets_actual - tweets_inicial

        signo_seguidores = "+" if variacion_seguidores >= 0 else ""
        signo_tweets = "+" if variacion_tweets >= 0 else ""

        texto_seguidores = f"{signo_seguidores}{variacion_seguidores:,} en el rango"
        texto_tweets = f"{signo_tweets}{variacion_tweets:,} en el rango"  # Modificado para mostrar el cambio en tweets

        resumenes.append(html.Div([
            html.Span(f"👤 {universidad} — ", style={'fontWeight': 'bold', 'fontSize': '18px'}),
            html.Span(f"📈 Seguidores actuales: {seguidores_actual:,} ({texto_seguidores}) — ", style={'fontSize': '16px'}),
            html.Span(f"📝 Tweets actuales: {tweets_actual:,} ({texto_tweets})", style={'fontSize': '16px'})
        ], style={'marginBottom': '20px', 'color': 'white'}))

    return html.Div(resumenes)

# Layout de la app
def crear_dashboard():
    app = Dash(__name__)
    app.title = "Dashboard Comparativo - Universidades X"

    # Obtener el rango de tiempo de las universidades
    rango_min_uni, rango_max_uni = obtener_rango_tiempo("UNI")
    rango_min_pucp, rango_max_pucp = obtener_rango_tiempo("PUCP")
    
    # El rango de tiempo más pequeño será el inicio, y el más grande el final
    rango_min = min(rango_min_uni, rango_min_pucp)
    rango_max = max(rango_max_uni, rango_max_pucp)

    print(f"Rango de tiempo UNI: {rango_min} - {rango_max}")

    # Layout de la app
    app.layout = html.Div([ 
        html.Div([  # Contenedor principal
            html.Div([  # Sección UNI (izquierda)
                html.H2("📊 Datos de la UNI", style={'color': '#FFD700', 'fontFamily': 'Arial', 'fontWeight': 'bold'}),
                html.Div(id='resumen-uni', style={'fontSize': '20px', 'marginBottom': '20px'}),
                dcc.Graph(id='grafico-uni-seguidores'),
                dcc.Graph(id='grafico-uni-tweets')
            ], style={'width': '45%', 'display': 'inline-block', 'vertical-align': 'top', 'padding': '20px', 
                      'backgroundColor': '#2F2F2F', 'borderRadius': '10px', 'boxShadow': '0px 4px 6px rgba(0, 0, 0, 0.1)'}),

            html.Div([  # Sección Comparativa (derecha)
                html.H2("📊 Comparación con Otras Universidades", style={'color': '#FFD700', 'fontFamily': 'Arial', 'fontWeight': 'bold'}),
                html.Div(id='resumen-comparativo', style={'fontSize': '20px', 'marginBottom': '20px'}),
                dcc.Graph(id='grafico-comparativo-seguidores'),
                dcc.Graph(id='grafico-comparativo-tweets')
            ], style={'width': '45%', 'display': 'inline-block', 'vertical-align': 'top', 'padding': '20px', 
                      'backgroundColor': '#2F2F2F', 'borderRadius': '10px', 'boxShadow': '0px 4px 6px rgba(0, 0, 0, 0.1)'}),
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'padding': '20px'}), 

        # Rango de tiempo (Slider) con las marcas de hora real
        html.Div([ 
            html.Label("Seleccione el rango de tiempo:", style={'color': 'white'}),
            dcc.RangeSlider(
                id='rango-tiempo',
                min=int(rango_min.timestamp()),  # Convertir la hora mínima en timestamp
                max=int(rango_max.timestamp()),  # Convertir la hora máxima en timestamp
                step=3600,  # Paso de una hora (en segundos)
                marks={
                    int(rango_min.timestamp()): {
                        'label': rango_min.strftime('%H:%M:%S') + '\n' + rango_min.strftime('%b %d'),  # Hora y fecha en dos líneas
                        'style': {'white-space': 'pre-line', 'white-space': 'nowrap'}
                    },
                    int(rango_max.timestamp()): {
                        'label': rango_max.strftime('%H:%M:%S') + '\n' + rango_max.strftime('%b %d'),  # Hora y fecha en dos líneas
                        'style': {'white-space': 'pre-line','white-space': 'nowrap'}
                    }
                },
                value=[int(rango_min.timestamp()), int(rango_max.timestamp())],  # Rango inicial
                tooltip={"placement": "bottom", "always_visible": False}  # No mostrar el número, solo la hora
            ),
        ], style={'padding': '20px', 'backgroundColor': '#2F2F2F', 'borderRadius': '10px'}),

        dcc.Interval(
            id='intervalo-actualizacion',
            interval=5 * 1000,  # Intervalo de 5 segundos
            n_intervals=0
        )
    ])

    # Callback para actualizar los datos y gráficos de la UNI
    @app.callback(
        Output('resumen-uni', 'children'),
        Output('grafico-uni-seguidores', 'figure'),
        Output('grafico-uni-tweets', 'figure'),
        Input('intervalo-actualizacion', 'n_intervals'),
        Input('rango-tiempo', 'value')  # Capturamos el valor del rango
    )
    def actualizar_uni(n, rango):
        try:
            universidad = "UNI"
            archivo_json = f'datos_json/seguidores_{universidad}.json'
            with open(archivo_json, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            # Convertir la lista de diccionarios a un DataFrame
            df = pd.DataFrame(datos)
            df['hora'] = pd.to_datetime(df['hora'], format='%d-%m-%Y %H:%M:%S')

            # Filtrar los datos según el rango de tiempo seleccionado
            df_filtrado = filtrar_datos_por_rango(df, rango)

            # Resumen de la UNI
            seguidores_actual = df_filtrado['seguidores'].iloc[-1]
            seguidores_inicial = df_filtrado['seguidores'].iloc[0]
            tweets_actual = df_filtrado['tweets'].iloc[-1]
            tweets_inicial = df_filtrado['tweets'].iloc[0]

            # Cálculo de variaciones
            variacion_seguidores = seguidores_actual - seguidores_inicial
            variacion_tweets = tweets_actual - tweets_inicial

            signo_seguidores = "+" if variacion_seguidores >= 0 else ""
            signo_tweets = "+" if variacion_tweets >= 0 else ""

            texto_seguidores = f"{signo_seguidores}{variacion_seguidores:,} en el rango"
            texto_tweets = f"{signo_tweets}{variacion_tweets:,} en el rango"  # Modificado para mostrar el cambio en tweets

            resumen_uni = html.Div([
                html.Span(f"👤 UNI — ", style={'fontWeight': 'bold'}),
                html.Span(f"📈 Seguidores actuales: {seguidores_actual:,} ({texto_seguidores}) — "),
                html.Span(f"📝 Tweets actuales: {tweets_actual:,} ({texto_tweets})")
            ], style={'color': 'white'})

            # Crear gráficos para la UNI
            grafico_seguidores = go.Figure()
            grafico_seguidores.add_trace(go.Scatter(
                x=df_filtrado['hora'],
                y=df_filtrado['seguidores'],
                mode='lines+markers',
                line=dict(color='#1E90FF'),
                name="Seguidores - UNI"
            ))
            grafico_seguidores.update_layout(
                title='Evolución de Seguidores de UNI',
                xaxis_title='Hora',
                yaxis_title='Seguidores',
                template='plotly_dark',
                yaxis_tickformat=","  # Mostrar números completos sin abreviaturas (sin 'k')
            )

            # Crear gráfico de tweets para UNI
            grafico_tweets = go.Figure()
            grafico_tweets.add_trace(go.Scatter(
                x=df_filtrado['hora'],
                y=df_filtrado['tweets'],
                mode='lines+markers',
                line=dict(color='#FFA500'),
                name="Tweets - UNI"
            ))
            grafico_tweets.update_layout(
                title=f'Evolución de Tweets de UNI ({texto_tweets})',  # Mostramos el cambio de tweets en el título
                xaxis_title='Hora',
                yaxis_title='Tweets',
                template='plotly_dark',
                yaxis_tickformat=",.0f",  # Asegurarnos de que los tweets sean números enteros sin decimales
                yaxis=dict(
                    tickmode='linear',  # Usar un modo lineal para el eje Y, evitando valores repetidos
                    tick0=0,  # Iniciar el eje Y en 0
                    dtick=1  # Ajustar el intervalo de los ticks en 1 para evitar repeticiones
                )
            )

            return resumen_uni, grafico_seguidores, grafico_tweets

        except Exception as e:
            error_texto = html.Div(f"Error al obtener datos de UNI: {e}", style={'color': 'red'})
            return error_texto, go.Figure(), go.Figure()

    # Callback para actualizar los gráficos y el resumen comparativo
    @app.callback(
        Output('resumen-comparativo', 'children'),
        Output('grafico-comparativo-seguidores', 'figure'),
        Output('grafico-comparativo-tweets', 'figure'),
        Input('intervalo-actualizacion', 'n_intervals'),
        Input('rango-tiempo', 'value')  # Capturamos el valor del rango
    )
    def actualizar_comparativo(n, rango):
        try:
            universidades = ["UNMSM", "UNFV", "PUCP", "UNI"]  # Incluimos la UNI en el comparativo también
            df_rango_universidades = {}

            # Aseguramos que el rango no se salga de los límites de los datos
            for universidad in universidades:
                archivo_json = f'datos_json/seguidores_{universidad}.json'
                with open(archivo_json, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    
                # Convertir la lista de diccionarios a un DataFrame
                df = pd.DataFrame(datos)
                df['hora'] = pd.to_datetime(df['hora'], format='%d-%m-%Y %H:%M:%S')

                # Filtrar los datos según el rango de tiempo seleccionado
                df_filtrado = filtrar_datos_por_rango(df, rango)
                df_rango_universidades[universidad] = df_filtrado

            resumen_comparativo = crear_resumen_comparativo(df_rango_universidades, universidades)
            grafico_seguidores = crear_grafico_comparativo(df_rango_universidades, universidades, "seguidores")
            grafico_tweets = crear_grafico_comparativo(df_rango_universidades, universidades, "tweets")

            return resumen_comparativo, grafico_seguidores, grafico_tweets

        except Exception as e:
            error_texto = html.Div(f"Error al obtener datos comparativos: {e}", style={'color': 'red'})
            return error_texto, go.Figure(), go.Figure()

    app.run(debug=True)

# Ejecutar la app
crear_dashboard()