import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px
from datetime import datetime, time
import re
import os

# Carregar dados
CSV_PATH = 'ligacoes_tratadas.csv'
df = pd.read_csv(CSV_PATH, sep=';', parse_dates=['Data'])

# Preprocessamento para performance
unique_destinos = df['destino_nome'].sort_values().unique()
min_date = df['Data'].min().date()
max_date = df['Data'].max().date()

# App Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'Painel de Monitoramento de Ligações - CBMMG'

# Logotipo
logo = html.Img(src='/assets/bombeiro.png', height='60px', style={'marginRight': '16px'})

# Filtros
filtros = dbc.Row([
    dbc.Col([logo], xs=12, md='auto', align='center', className='my-2'),
    dbc.Col([
        html.H2('Painel de Monitoramento Central Telefônica', className='titulo-topo mb-2', style={'marginBottom': 0}),
        html.H2('5ºCOB (Ipatinga)', className='titulo-topo mb-2', style={'marginBottom': 0}),
        html.H5('Corpo de Bombeiros Militar de Minas Gerais', className='titulo-topo mb-2', style={'marginTop': 0})
    ], xs=12, md=6, align='center', className='my-2'),
], align='center', className='my-2')

filtros2 = dbc.Row([
    dbc.Col([
        html.Label('Data Inicial', style={'color': '#fff'}),
        dcc.DatePickerSingle(
            id='date-inicio',
            min_date_allowed=min_date,
            max_date_allowed=max_date,
            date=min_date,
            display_format='DD/MM/YYYY',
            style={'width': '100%'}
        ),
        dbc.Row([
            dbc.Col(dcc.Input(
                id='hh-inicio',
                type='number',
                min=0, max=23, step=1, inputMode='numeric', maxLength=2,
                value=0,
                style={'width': '100%', 'textAlign': 'center'}
            ), xs=5, md=4, className='my-2'),
            dbc.Col(html.Div(':', style={'textAlign': 'center', 'fontWeight': 'bold', 'fontSize': 22, 'color': '#fff'}), xs=2, md=1, className='my-2'),
            dbc.Col(dcc.Input(
                id='mm-inicio',
                type='number',
                min=0, max=59, step=1, inputMode='numeric', maxLength=2,
                value=0,
                style={'width': '100%', 'textAlign': 'center'}
            ), xs=5, md=4, className='my-2'),
        ], style={'marginTop': 4, 'marginBottom': 0, 'alignItems': 'center'}, justify='start'),
        html.Small('Ex: 08:30', style={'color': '#fff'})
    ], xs=12, md=2, className='my-2'),
    dbc.Col([
        html.Label('Data Final', style={'color': '#fff'}),
        dcc.DatePickerSingle(
            id='date-fim',
            min_date_allowed=min_date,
            max_date_allowed=max_date,
            date=max_date,
            display_format='DD/MM/YYYY',
            style={'width': '100%'}
        ),
        dbc.Row([
            dbc.Col(dcc.Input(
                id='hh-fim',
                type='number',
                min=0, max=23, step=1, inputMode='numeric', maxLength=2,
                value=23,
                style={'width': '100%', 'textAlign': 'center'}
            ), xs=5, md=4, className='my-2'),
            dbc.Col(html.Div(':', style={'textAlign': 'center', 'fontWeight': 'bold', 'fontSize': 22, 'color': '#fff'}), xs=2, md=1, className='my-2'),
            dbc.Col(dcc.Input(
                id='mm-fim',
                type='number',
                min=0, max=59, step=1, inputMode='numeric', maxLength=2,
                value=59,
                style={'width': '100%', 'textAlign': 'center'}
            ), xs=5, md=4, className='my-2'),
        ], style={'marginTop': 4, 'marginBottom': 0, 'alignItems': 'center'}, justify='start'),
        html.Small('Ex: 08:30', style={'color': '#fff'})
    ], xs=12, md=2, className='my-2'),
    dbc.Col([
        dcc.Dropdown(
            id='destino-dropdown',
            options=[{'label': d, 'value': d} for d in unique_destinos],
            value=list(unique_destinos),
            multi=True,
            placeholder='Filtrar por Destino',
            style={'width': '100%', 'marginTop': 24}
        )
    ], xs=12, md=4, className='my-2'),
], className='mb-4')

# Indicadores principais
indicadores = dbc.Row([
    dbc.Col(dbc.Card([dbc.CardBody([
        html.H6('Total de Ligações', className='card-title'),
        html.H2(id='total-ligacoes', className='card-text')
    ])]), xs=12, md=4, className='my-2'),
    dbc.Col(dbc.Card([dbc.CardBody([
        html.H6('Atendidas', className='card-title'),
        html.H2(id='total-atendidas', className='card-text')
    ])]), xs=12, md=4, className='my-2'),
    dbc.Col(dbc.Card([dbc.CardBody([
        html.H6('Não Atendidas', className='card-title'),
        html.H2(id='total-nao-atendidas', className='card-text')
    ])]), xs=12, md=4, className='my-2'),
], className='mb-3')

# Indicadores avançados
indicadores_avancados = dbc.Row([
    dbc.Col(dbc.Card([dbc.CardBody([
        html.H6('Taxa de Atendimento', className='card-title'),
        html.H2(id='taxa-atendimento', className='card-text')
    ])]), xs=12, md=4, className='my-2'),
    dbc.Col(dbc.Card([dbc.CardBody([
        html.H6('Duração Média (s) - Atendidas', className='card-title'),
        html.H2(id='duracao-media', className='card-text')
    ])]), xs=12, md=4, className='my-2'),
    dbc.Col(dbc.Card([dbc.CardBody([
        html.H6('Total de Tempo Falado/dia', className='card-title'),
        html.H2(id='total-segundos-dia', className='card-text')
    ])]), xs=12, md=4, className='my-2'),
], className='mb-4')

# Gráficos
graficos = dbc.Row([
    dbc.Col(dcc.Graph(id='grafico-linha-dia', className='my-2'), xs=12, md=6, className='my-2'),
    dbc.Col(dcc.Graph(id='grafico-barra-faixa', className='my-2'), xs=12, md=6, className='my-2'),
], className='mb-4')

graficos2 = dbc.Row([
    dbc.Col(dcc.Graph(id='heatmap-hora-dia', className='my-2'), xs=12, md=6, className='my-2'),
    dbc.Col(dcc.Graph(id='grafico-comparativo-tipo-dia', className='my-2'), xs=12, md=6, className='my-2'),
], className='mb-4')

# Layout
app.layout = dbc.Container([
    filtros,
    filtros2,
    indicadores,
    indicadores_avancados,
    graficos,
    graficos2,
    html.Footer([
        html.Hr(),
        html.P('Desenvolvido para o Corpo de Bombeiros Militar de Minas Gerais', style={'textAlign': 'center', 'color': '#fff'})
    ], className='footer')
], fluid=True, id='main-container')

# Função para converter segundos em formato legível
def segundos_legiveis(segundos):
    segundos = int(segundos)
    if segundos < 60:
        return f"{segundos}s"
    minutos = segundos // 60
    s = segundos % 60
    if minutos < 60:
        return f"{minutos}min {s}s" if s else f"{minutos}min"
    horas = minutos // 60
    m = minutos % 60
    return f"{horas}h {m}min {s}s" if s else (f"{horas}h {m}min" if m else f"{horas}h")

# Callback
@app.callback(
    [
        Output('total-ligacoes', 'children'),
        Output('total-atendidas', 'children'),
        Output('total-nao-atendidas', 'children'),
        Output('taxa-atendimento', 'children'),
        Output('taxa-atendimento', 'style'),
        Output('duracao-media', 'children'),
        Output('duracao-media', 'style'),
        Output('total-segundos-dia', 'children'),
        Output('grafico-linha-dia', 'figure'),
        Output('grafico-barra-faixa', 'figure'),
        Output('heatmap-hora-dia', 'figure'),
        Output('grafico-comparativo-tipo-dia', 'figure'),
    ],
    [
        Input('date-inicio', 'date'),
        Input('hh-inicio', 'value'),
        Input('mm-inicio', 'value'),
        Input('date-fim', 'date'),
        Input('hh-fim', 'value'),
        Input('mm-fim', 'value'),
        Input('destino-dropdown', 'value'),
    ]
)
def atualizar_dashboard(date_ini, hh_ini, mm_ini, date_fim, hh_fim, mm_fim, destinos):
    # Validação dos campos de hora/minuto
    try:
        hh_ini = int(hh_ini)
        if not (0 <= hh_ini <= 23):
            hh_ini = 0
    except:
        hh_ini = 0
    try:
        mm_ini = int(mm_ini)
        if not (0 <= mm_ini <= 59):
            mm_ini = 0
    except:
        mm_ini = 0
    try:
        hh_fim = int(hh_fim)
        if not (0 <= hh_fim <= 23):
            hh_fim = 23
    except:
        hh_fim = 23
    try:
        mm_fim = int(mm_fim)
        if not (0 <= mm_fim <= 59):
            mm_fim = 59
    except:
        mm_fim = 59
    hora_ini = f'{hh_ini:02d}:{mm_ini:02d}'
    hora_fim = f'{hh_fim:02d}:{mm_fim:02d}'
    # Combinar data e hora
    try:
        datahora_ini = datetime.strptime(f"{date_ini} {hora_ini}", "%Y-%m-%d %H:%M")
    except:
        datahora_ini = df['Data'].min()
    try:
        datahora_fim = datetime.strptime(f"{date_fim} {hora_fim}", "%Y-%m-%d %H:%M")
    except:
        datahora_fim = df['Data'].max()

    dff = df[(df['Data'] >= datahora_ini) & (df['Data'] <= datahora_fim)]
    if destinos:
        dff = dff[dff['destino_nome'].isin(destinos)]

    # Indicadores principais
    total = len(dff)
    atendidas = dff['atendida'].sum()
    nao_atendidas = total - atendidas
    taxa = (atendidas / total * 100) if total > 0 else 0
    taxa_str = f'{taxa:.1f}%'
    taxa_style = {'color': 'red' if taxa < 85 else '#162447', 'fontWeight': 'bold'}

    # Indicadores avançados
    atendidas_df = dff[dff['atendida'] == 1]
    duracao_media = atendidas_df['duracao_segundos'].mean() if not atendidas_df.empty else 0
    duracao_media_str = segundos_legiveis(duracao_media)
    duracao_style = {'color': 'orange', 'fontWeight': 'bold'} if duracao_media > 300 else {'color': '#162447', 'fontWeight': 'bold'}
    total_seg_dia = atendidas_df.groupby('data')['duracao_segundos'].sum().mean() if not atendidas_df.empty else 0
    total_seg_dia_str = segundos_legiveis(total_seg_dia)

    # Função para gráfico vazio
    def grafico_vazio(titulo):
        return {
            'data': [],
            'layout': {
                'xaxis': {'visible': False},
                'yaxis': {'visible': False},
                'annotations': [{
                    'text': 'Sem dados para exibir',
                    'xref': 'paper', 'yref': 'paper',
                    'showarrow': False,
                    'font': {'size': 18, 'color': '#a84105'}
                }],
                'plot_bgcolor': '#fff',
                'paper_bgcolor': '#fff',
                'title': {'text': titulo, 'font': {'color': '#162447'}},
                'font': {'color': '#162447'}
            }
        }

    # Gráfico de linha: ligações por dia
    lig_dia = dff.groupby('data').size().reset_index(name='Ligações')
    if not lig_dia.empty:
        fig_linha = px.line(lig_dia, x='data', y='Ligações', markers=True, title='Ligações por Dia', template='plotly')
        fig_linha.update_traces(line_color='#a84105', marker_color='#162447', marker_line_color='#a84105', marker_line_width=2)
        fig_linha.update_layout(
            margin=dict(l=0, r=0, t=40, b=0),
            font_color='#162447',
            title_font_color='#a84105'
        )
    else:
        fig_linha = grafico_vazio('Ligações por Dia')

    # Gráfico de barras: ligações por faixa horária
    lig_faixa = dff.groupby('faixa_horaria').size().reindex([
        '00–02h','02–04h','04–06h','06–08h','08–10h','10–12h','12–14h','14–16h','16–18h','18–20h','20–22h','22–24h'
    ]).fillna(0).reset_index(name='Ligações')
    if lig_faixa['Ligações'].sum() > 0:
        fig_barra = px.bar(lig_faixa, x='faixa_horaria', y='Ligações', title='Ligações por Faixa Horária', template='plotly')
        fig_barra.update_traces(marker_line_color='#a84105', marker_line_width=2, marker_color='#a84105', text=lig_faixa['Ligações'], textposition='outside')
        fig_barra.update_layout(
            margin=dict(l=0, r=0, t=40, b=0), xaxis_title='Faixa Horária',
            font_color='#162447',
            title_font_color='#a84105',
            yaxis=dict(title='Ligações', showgrid=True, gridcolor='#eee'),
            xaxis=dict(showgrid=False),
            uniformtext_minsize=8, uniformtext_mode='hide'
        )
    else:
        fig_barra = grafico_vazio('Ligações por Faixa Horária')

    # Heatmap: Hora vs Dia da Semana
    heat = dff.groupby(['dia_semana','hora']).size().reset_index(name='Ligações')
    dias_ordem = ['Segunda-feira','Terça-feira','Quarta-feira','Quinta-feira','Sexta-feira','Sábado','Domingo']
    heat['hora'] = heat['hora'].astype(str)
    if not heat.empty:
        fig_heat = px.density_heatmap(heat, x='hora', y='dia_semana', z='Ligações',
            category_orders={'dia_semana': dias_ordem}, color_continuous_scale=['#fff', '#a84105', '#162447'], title='Heatmap Hora x Dia da Semana', template='plotly')
        fig_heat.update_layout(
            margin=dict(l=0, r=0, t=40, b=0), font_color='#162447', title_font_color='#a84105'
        )
    else:
        fig_heat = grafico_vazio('Heatmap Hora x Dia da Semana')

    # Comparativo Dias Úteis vs Finais de Semana
    comp = dff.groupby('tipo_dia').size().reset_index(name='Ligações')
    if not comp.empty:
        fig_comp = px.pie(comp, names='tipo_dia', values='Ligações', title='Dias Úteis vs Finais de Semana',
            color='tipo_dia', color_discrete_map={'Dia útil':'#fff','Final de semana':'#a84105'}, template='plotly')
        fig_comp.update_traces(textinfo='percent+label', textfont_color='#162447', marker=dict(line=dict(color='#162447', width=2)))
        fig_comp.update_layout(
            margin=dict(l=0, r=0, t=40, b=0), font_color='#162447', title_font_color='#a84105', legend_font_color='#162447'
        )
    else:
        fig_comp = grafico_vazio('Dias Úteis vs Finais de Semana')

    return (
        f'{total:,}',
        f'{atendidas:,}',
        f'{nao_atendidas:,}',
        taxa_str,
        taxa_style,
        duracao_media_str,
        duracao_style,
        total_seg_dia_str,
        fig_linha,
        fig_barra,
        fig_heat,
        fig_comp
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host="0.0.0.0", port=port, debug=True)