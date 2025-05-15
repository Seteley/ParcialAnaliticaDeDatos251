from dash import Dash, html, dcc, Input, Output, State
from datetime import datetime
import plotly.graph_objs as go
import os
import json
import pandas as pd

app = Dash(__name__)
app.title = "Dashboard X"

# 🧠 Función 1: Crear resumen textual
def crear_resumen(usuario, seguidores_actual, seguidores_inicial):
    variacion = seguidores_actual - seguidores_inicial
    signo = "+" if variacion >= 0 else ""
    texto_variacion = f"{signo}{variacion:,} seguidores en el rango seleccionado"

    return html.Div([
        html.Span(f"👤 @{usuario} — "),
        html.Span(f"📈 Seguidores actuales: {seguidores_actual:,} — "),
        html.Span(f"📊 Variación: {texto_variacion}")
    ])

# 📈 Función 2: Crear gráfico
def crear_grafico(df_rango, usuario):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_rango['hora'].dt.strftime('%H:%M:%S'),
        y=df_rango['seguidores'],
        mode='lines+markers',
        line=dict(color='blue'),
        name='Seguidores'
    ))

    fig.update_layout(
        xaxis_title='Hora',
        yaxis_title='Seguidores',
        title=f'Evolución de seguidores de @{usuario}',
        template='plotly_white'
    )
    return fig

# 🎯 Función 3: Crear barra de meta
def crear_barra_meta(meta, seguidores_actual):
    if meta and meta > 0:
        porcentaje = min((seguidores_actual / meta) * 100, 100)
        faltan = max(meta - seguidores_actual, 0)
        return html.Div([
            html.P(f"📌 Meta: {meta:,} seguidores"),
            html.P(f"🚀 Progreso: {porcentaje:.2f}% — Faltan {faltan:,} seguidores"),
            html.Div(
                style={
                    'background': '#e0e0e0',
                    'borderRadius': '5px',
                    'height': '20px',
                    'width': '100%',
                    'marginTop': '5px'
                },
                children=html.Div(
                    style={
                        'background': '#4caf50',
                        'width': f'{porcentaje}%',
                        'height': '100%',
                        'borderRadius': '5px'
                    }
                )
            )
        ])
    else:
        return html.Div("⚠️ Define una meta válida.")

# Layout principal
app.layout = html.Div([
    html.H1("📊 Seguidores en Tiempo Real - Twitter (X)"),

    dcc.Input(
        id='usuario-twitter',
        type='text',
        value='elonmusk',
        debounce=True,
        placeholder='Nombre de usuario (sin @)',
        style={'marginBottom': '20px', 'width': '300px'}
    ),

    html.Div(id='datos-actuales', style={'fontSize': '20px', 'marginBottom': '20px'}),

    html.Div([
        html.Label("🎯 Define tu meta de seguidores:", style={'fontWeight': 'bold'}),
        dcc.Input(
            id='meta-seguidores',
            type='number',
            placeholder='Ej: 100000',
            value=500000,
            style={'marginBottom': '20px', 'width': '200px'}
        ),
        html.Div(id='progreso-meta', style={'marginBottom': '30px'})
    ]),

    dcc.Graph(id='grafico-seguidores'),

    dcc.RangeSlider(id='rango-tiempo', step=1, allowCross=False, tooltip={"placement": "bottom", "always_visible": True}),

    dcc.Interval(
        id='intervalo-actualizacion',
        interval=5 * 1000,
        n_intervals=0
    )
])

# Slider de tiempo
@app.callback(
    Output('rango-tiempo', 'min'),
    Output('rango-tiempo', 'max'),
    Output('rango-tiempo', 'value'),
    Output('rango-tiempo', 'marks'),
    Input('intervalo-actualizacion', 'n_intervals'),
    Input('usuario-twitter', 'value')
)
def actualizar_slider(n, usuario):
    archivo_json = f'datos_json/seguidores_{usuario}.json'
    try:
        with open(archivo_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)

        df = pd.DataFrame(datos)
        df['hora'] = pd.to_datetime(df['hora'])
        df = df.sort_values('hora')

        horas_str = df['hora'].dt.strftime('%H:%M:%S').tolist()
        total = len(horas_str)
        min_idx, max_idx = 0, total - 1
        marks = {i: hora for i, hora in enumerate(horas_str) if i % max(1, total // 10) == 0}

        return min_idx, max_idx, [min_idx, max_idx], marks

    except Exception:
        return 0, 1, [0, 1], {}

# Callback principal: actualiza resumen, gráfica y meta
@app.callback(
    Output('datos-actuales', 'children'),
    Output('grafico-seguidores', 'figure'),
    Output('progreso-meta', 'children'),
    Input('intervalo-actualizacion', 'n_intervals'),
    Input('usuario-twitter', 'value'),
    Input('rango-tiempo', 'value'),
    Input('meta-seguidores', 'value')
)
def actualizar_dashboard(n, usuario, rango, meta):
    try:
        archivo_json = f'datos_json/seguidores_{usuario}.json'

        if not os.path.exists(archivo_json):
            raise FileNotFoundError(f"No se encontró el archivo: {archivo_json}")

        with open(archivo_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)

        if not datos:
            raise ValueError("El archivo está vacío.")

        df = pd.DataFrame(datos)
        df['hora'] = pd.to_datetime(df['hora'])
        df = df.sort_values('hora')

        i_ini, i_fin = rango if rango else (0, len(df)-1)
        df_rango = df.iloc[i_ini:i_fin+1]

        seguidores_actual = df_rango['seguidores'].iloc[-1]
        seguidores_inicial = df_rango['seguidores'].iloc[0]

        resumen = crear_resumen(usuario, seguidores_actual, seguidores_inicial)
        grafico = crear_grafico(df_rango, usuario)
        barra_progreso = crear_barra_meta(meta, seguidores_actual)

        return resumen, grafico, barra_progreso

    except Exception as e:
        error_texto = html.Div(f"Error al obtener datos de @{usuario}: {e}", style={'color': 'red'})
        return error_texto, go.Figure(), html.Div()

if __name__ == '__main__':
    app.run(debug=True)
