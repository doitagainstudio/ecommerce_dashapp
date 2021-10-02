import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input
import plotly.graph_objs as go

# Collegamento al file esterno
df = pd.read_pickle("./data/processed/summary.pkl")

# Definizione del Fatturato Netto
FattNegativo = abs(df['ImportoNetto']) * (-1)
df['FatturatoNetto'] = np.where(df['Quantita'] < 0, FattNegativo, abs(df['ImportoNetto']))
df['FatturatoNetto'] = np.where(df['Documento_Numero'].str.contains("B") == True, 0, df['FatturatoNetto'])

# Definizione del Costo Prodotto
CostoProdottoNeg = abs(df['Prodotto_Costoattuale']) * (-1)
df['CostoProdotto'] = np.where(df['Quantita'] < 0, CostoProdottoNeg, abs(df['Prodotto_Costoattuale']))
df['CostoProdotto'] = np.where(df['Documento_Numero'].str.contains("B") == True, 0, df['CostoProdotto'])

# Indicizziamo il DataFrame in base al campo della data
# df['DataRiferimento'] = pd.to_datetime(df.DataRiferimento)
df = df.set_index('DataRiferimento')

# Definiamo i principali KPI

# Fatturato
Fatturato = df['FatturatoNetto'].resample('M').sum()

# Guadagno
df['Guadagno'] = round(df['FatturatoNetto'] - df['CostoProdotto'], 2)
Guadagno = df['Guadagno'].resample('M').sum()

# Margine
Margine = round(Guadagno / Fatturato * 100, 2)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], meta_tags=[{'name': 'viewport',
                                                                                   'content': 'width=device-width, initial-scale=1.0'}])

app.title = 'Doitagain E-Commerce Dashboard'
app.layout = html.Div([
    html.H1('E-Commerce Performances Dashboard', style={'fontWeight': 'bold'}),
    html.H2('Econometrics Data Analysis'),
    html.Br(),
    html.Ul([
        html.Li('Per iniziare, selezionare un anno dal menu a tendina.'),
        html.Li('Cliccare sulle schede per il monitoraggio dei principali KPI.'),
        html.Li(['Fonte dati principale: ', html.A('HERE', href='https://www.doitagainstudio.com')])
    ]),
    dcc.Dropdown(id='year_dropdown',
                 options=[{'label': year, 'value': year} for year in df.index.year.unique()],
                 placeholder='Selezionare un anno'),
    html.Br(),
    dbc.Tabs([
        dbc.Tab([
            html.H3('Fatturato per anno di riferimento'),
            html.Br(),
            html.Div(id='fatturato'),
            html.Br(),
            dcc.Graph(id='fatturato_graph')
        ], label="Fatturato"),
        dbc.Tab([
            html.H3('Margine per anno di riferimento'),
            html.Br(),
            html.Div(id='margine'),
            html.Br(),
            dcc.Graph(id='margine_graph')
        ], label="Margine")
    ])
])


@app.callback(Output('fatturato', 'children'), Output('fatturato_graph', 'figure'), Output('margine_graph', 'figure'),
              [Input('year_dropdown', 'value')])
def display_info(year):
    fatturato_fig = go.Figure()
    margine_fig = go.Figure()
    if year is not None:
        previous_year = year - 1
        fatturato_fig.add_scatter(x=Fatturato[str(year)].index.month_name(locale='Italian'),
                                  y=round(Fatturato[str(year)], 2),
                                  name=str(year), hovertemplate='€ %{y:.2f}' + '<br>%{x}')
        margine_fig.add_scatter(x=Margine[str(year)].index.month_name(locale='Italian'),
                                y=round(Margine[str(year)], 2),
                                name=str(year), hovertemplate='%{y:.2f} %' + '<br>%{x}')
        if (previous_year) in Fatturato.index.year:
            fatturato_fig.add_scatter(x=Fatturato[str(previous_year)].index.month_name(locale='Italian'),
                                      y=round(Fatturato[str(previous_year)], 2),
                                      name=str(previous_year), hovertemplate='€ %{y:.2f}' + '<br>%{x}')
            margine_fig.add_scatter(x=Margine[str(previous_year)].index.month_name(locale='Italian'),
                                    y=round(Margine[str(previous_year)], 2),
                                    name=str(previous_year), hovertemplate='%{y:.2f} %' + '<br>%{x}')
        fatturato_fig.update_yaxes(title_text='Fatturato')
        margine_fig.update_yaxes(title_text='Margine')
        return ['Il fatturato per l\'anno selezionato è pari a € ' + str(round(Fatturato[str(year)].sum(), 2)),
                fatturato_fig, margine_fig]
    else:
        return ['Scegliere un anno dal menu a tendina', fatturato_fig, margine_fig]


if __name__ == '__main__':
    app.run_server(debug=True)
