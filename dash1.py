from dash import Dash, html, dcc, Input, Output
from unofficial_livecounts_api.twitter import TwitterAgent
from datetime import datetime
import plotly.graph_objs as go

app = Dash(__name__)
app.title = "Dashboard Seguidores en Tiempo Real"

# Variables globales (en memoria)
historico_tiempos = []
historico_seguidores = []
primer_valor = {}

# Layout
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

    dcc.Graph(id='grafico-seguidores'),

    dcc.Interval(
        id='intervalo-actualizacion',
        interval=5 * 1000,  # cada 5 segundos
        n_intervals=0
    )
])

@app.callback(
    Output('datos-actuales', 'children'),
    Output('grafico-seguidores', 'figure'),
    Input('intervalo-actualizacion', 'n_intervals'),
    Input('usuario-twitter', 'value')
)
def actualizar_dashboard(n, usuario):
    global historico_tiempos, historico_seguidores, primer_valor

    try:
        # Obtener métricas
        metricas = TwitterAgent.fetch_user_metrics(query=usuario)
        seguidores_actual = metricas.follower_count
        hora = datetime.now().strftime('%H:%M:%S')

        # Inicializa si es la primera vez
        if usuario not in primer_valor:
            primer_valor[usuario] = seguidores_actual
            historico_tiempos.clear()
            historico_seguidores.clear()

        # Actualiza historial
        historico_tiempos.append(hora)
        historico_seguidores.append(seguidores_actual)

        # Solo guardar los últimos 30
        historico_tiempos[:] = historico_tiempos[-30:]
        historico_seguidores[:] = historico_seguidores[-30:]

        # Cálculo de variación
        variacion = seguidores_actual - primer_valor[usuario]
        signo = "+" if variacion >= 0 else ""
        texto_variacion = f"{signo}{variacion:,} seguidores desde el inicio"

        # Texto resumen
        resumen = html.Div([
            html.Span(f"👤 @{usuario} — "),
            html.Span(f"📈 Seguidores actuales: {seguidores_actual:,} — "),
            html.Span(f"📊 Variación: {texto_variacion}")
        ])

        # Gráfico
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=historico_tiempos,
            y=historico_seguidores,
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

        return resumen, fig

    except Exception as e:
        error_texto = html.Div(f"Error al obtener datos de @{usuario}: {e}", style={'color': 'red'})
        return error_texto, go.Figure()

# Ejecutar app
if __name__ == '__main__':
    app.run(debug=True)
