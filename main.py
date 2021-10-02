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

### KPI SECTION
# -------------------------------------------------------

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

# # Fatturato
# Fatturato = df['FatturatoNetto'].resample('M').sum()
#
# # Guadagno
# df['Guadagno'] = round(df['FatturatoNetto'] - df['CostoProdotto'], 2)
# Guadagno = df['Guadagno'].resample('M').sum()
#
# # Margine
# Margine = round(Guadagno / Fatturato * 100, 2)

# # Usiamo le tabelle pivot per avere un'organizzazione migliore dei dati
# ## Tabella delle vendite generiche
# sales_tot = pd.pivot_table(df, index=df.index.month, columns=df.index.year, values=['FatturatoNetto', 'Guadagno'],
#                            aggfunc=sum)
#
# ## Tabella delle vendite indicizzate per marketplace
# sales_mktpl = pd.pivot_table(df, index=[df.index.month, df.Origine], columns=df.index.year,
#                              values=['FatturatoNetto', 'Guadagno'], aggfunc='sum')
#
# # Definiamo il numero degli ordini
## Filtriamo il DataFrame per individuare gli ordini e le fatture validi
ordini_filt = df[(df['Documento_Numero'].str.contains('A|B') == False) & (df['Quantita'] > 0)]
# margine_tbl = round(ordini_filt['Guadagno'] / ordini_filt['FatturatoNetto'] * 100, 2)
#
# # ordini_filt.loc['Margine %'] = ordini_filt.loc['Guadagno'] / ordini_filt.loc['FatturatoNetto']
# fatture_filt = df[(df['Documento_Numero'].str.contains('F') == True) & (df['Quantita'] > 0)]
#
# ## Tabella ordini indicizzate per marketplace
# ordini_tbl_mktpl = pd.pivot_table(ordini_filt, index=[ordini_filt.index.month, ordini_filt.Origine],
#                                   columns=ordini_filt.index.year, values='Documento_Numero', aggfunc=pd.Series.nunique)
#
# ## Tabella ordini generici
# ordini_tbl = pd.pivot_table(ordini_filt, index=ordini_filt.index.month, columns=ordini_filt.index.year,
#                             values='Documento_Numero', aggfunc=pd.Series.nunique)

### LAYOUT SECTION
# ---------------------------------------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE], meta_tags=[{'name': 'viewport',
                                                                               'content': 'width=device-width, initial-scale=1.0'}])

app.title = 'Doitagain E-Commerce Dashboard'
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([

        ], width=2),
        dbc.Col([
            html.H1('E-Commerce Performances Dashboard', className='text-center font-weight-bolder text-primary'),
            html.H2('Econometrics Data Analysis', className='text-center mb-4'),
            html.Br()
        ], width=8),
        dbc.Col([

        ], width=2)
    ]),
    dbc.Row([
        dbc.Col([
            html.Ul([
                html.Li('Per iniziare, selezionare un anno dal menu a tendina.'),
                html.Li('Cliccare sulle schede per il monitoraggio dei principali KPI.'),
                html.Li(['Fonte dati principale: ', html.A('HERE', href='https://www.doitagainstudio.com')])
            ], className='text-left')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id='year_dropdown',
                         options=[{'label': 'Anno ' + str(year), 'value': year} for year in
                                  sorted(df.index.year.unique())],
                         placeholder='Anno'),
            html.Br(),
        ], xs=5, sm=5, md=5, lg=2, xl=2),
        dbc.Col([
            dcc.Dropdown(id='channel_dropdown',
                         placeholder='Origine'),
            html.Br(),
        ], id='origine', xs=5, sm=5, md=5, lg=2, xl=2)
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id='fatturato', className='font-weight-bold'),
            html.Br(),
            html.Div(id='mktpl', className='font-weight-bold'),
            html.Br(),
            html.Div(id='ordini', className='font-weight-bold'),
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Tabs([
                dbc.Tab([
                    dbc.Row([
                        dbc.Col([
                            html.Br(),
                            html.H3('Fatturato per anno di riferimento'),
                        ])
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='fatturato_graph')
                        ]),
                    ], justify='around')
                ], label="Fatturato"),
                dbc.Tab([
                    dbc.Row([
                        dbc.Col([
                            html.Br(),
                            html.H3('Margine per anno di riferimento'),
                        ])
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='margine_graph')
                        ]),
                    ], justify='around')
                ], label="Margine"),
                dbc.Tab([
                    dbc.Row([
                        dbc.Col([
                            html.Br(),
                            html.H3('Ordini per anno di riferimento'),
                        ])
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='ordini_graph')
                        ]),
                    ], justify='around')
                ], label="Ordini")
            ])
        ], xs=12, sm=12, md=8, lg=8, xl=8),
        dbc.Col([

        ], width=4)
    ])
])


@app.callback(Output('fatturato', 'children'), Output('fatturato_graph', 'figure'), Output('margine_graph', 'figure'),
              Output('ordini_graph', 'figure'),
              Output('origine', 'children'), Output('mktpl', 'children'), Output('ordini', 'children'),
              [Input('year_dropdown', 'value'), Input('channel_dropdown', 'value')])
def display_info(year, channel):
    fatturato_fig = go.Figure()
    margine_fig = go.Figure()
    ordini_fig = go.Figure()
    mktpl = 'Scegliere un\'origine dal menù a tendina'
    fatturato = 'Selezionare un anno dal menù a tendina'
    ordini = ''
    if year is not None:
        if channel is not None:
            previous_year = year - 1
            dff = df[df['Origine'] == channel].copy()
            Fatturato = dff['FatturatoNetto'].resample('M').sum()
            dff['Guadagno'] = round(dff['FatturatoNetto'] - dff['CostoProdotto'], 2)
            Guadagno = dff['Guadagno'].resample('M').sum()
            Margine = round(Guadagno / Fatturato * 100, 2)
            ordini_filt = dff[(dff['Documento_Numero'].str.contains('A|B') == False) & (dff['Quantita'] > 0)]
            numero_ordini = ordini_filt['Documento_Numero'].resample('M').nunique()
            fatturato_fig.add_scatter(x=Fatturato.loc[str(year)].index.month_name(locale='Italian'),
                                      y=round(Fatturato.loc[str(year)], 2),
                                      name=str(year), hovertemplate='€ %{y:.2f}' + '<br>%{x}')
            margine_fig.add_scatter(x=Margine[str(year)].index.month_name(locale='Italian'),
                                    y=round(Margine.loc[str(year)], 2),
                                    name=str(year), hovertemplate='%{y:.2f} %' + '<br>%{x}')
            ordini_fig.add_scatter(x=numero_ordini.loc[str(year)].index.month_name(locale='Italian'),
                                   y=round(numero_ordini.loc[str(year)], 2),
                                   name=str(year), hovertemplate='%{y:.0f}' + '<br>%{x}')
            if (previous_year) in Fatturato.index.year:
                fatturato_fig.add_scatter(x=Fatturato.loc[str(previous_year)].index.month_name(locale='Italian'),
                                          y=round(Fatturato.loc[str(previous_year)], 2),
                                          name=str(previous_year), hovertemplate='€ %{y:.2f}' + '<br>%{x}')
                margine_fig.add_scatter(x=Margine.loc[str(previous_year)].index.month_name(locale='Italian'),
                                        y=round(Margine.loc[str(previous_year)], 2),
                                        name=str(previous_year), hovertemplate='%{y:.2f} %' + '<br>%{x}')
                ordini_fig.add_scatter(x=numero_ordini.loc[str(previous_year)].index.month_name(locale='Italian'),
                                       y=round(numero_ordini.loc[str(previous_year)], 2),
                                       name=str(previous_year), hovertemplate='%{y:.0f}' + '<br>%{x}')
            fatturato_fig.update_yaxes(title_text='Fatturato')
            margine_fig.update_yaxes(title_text='Margine')
            ordini_fig.update_yaxes(title_text='N. Ordini')
            mktpl = 'Origine: ' + str(channel)
        else:
            previous_year = year - 1
            Fatturato = df['FatturatoNetto'].resample('M').sum()
            df['Guadagno'] = round(df['FatturatoNetto'] - df['CostoProdotto'], 2)
            Guadagno = df['Guadagno'].resample('M').sum()
            Margine = round(Guadagno / Fatturato * 100, 2)
            ordini_filt = df[(df['Documento_Numero'].str.contains('A|B') == False) & (df['Quantita'] > 0)]
            numero_ordini = ordini_filt['Documento_Numero'].resample('M').nunique()
            fatturato_fig.add_scatter(x=Fatturato.loc[str(year)].index.month_name(locale='Italian'),
                                      y=round(Fatturato.loc[str(year)], 2),
                                      name=str(year), hovertemplate='€ %{y:.2f}' + '<br>%{x}')
            margine_fig.add_scatter(x=Margine.loc[str(year)].index.month_name(locale='Italian'),
                                    y=round(Margine.loc[str(year)], 2),
                                    name=str(year), hovertemplate='%{y:.2f} %' + '<br>%{x}')
            ordini_fig.add_scatter(x=numero_ordini.loc[str(year)].index.month_name(locale='Italian'),
                                   y=round(numero_ordini.loc[str(year)], 2),
                                   name=str(year), hovertemplate='%{y:.0f}' + '<br>%{x}')
            if (previous_year) in Fatturato.index.year:
                fatturato_fig.add_scatter(x=Fatturato.loc[str(previous_year)].index.month_name(locale='Italian'),
                                          y=round(Fatturato.loc[str(previous_year)], 2),
                                          name=str(previous_year), hovertemplate='€ %{y:.2f}' + '<br>%{x}')
                margine_fig.add_scatter(x=Margine[str(previous_year)].index.month_name(locale='Italian'),
                                        y=round(Margine[str(previous_year)], 2),
                                        name=str(previous_year), hovertemplate='%{y:.2f} %' + '<br>%{x}')
                ordini_fig.add_scatter(x=numero_ordini.loc[str(previous_year)].index.month_name(locale='Italian'),
                                       y=round(numero_ordini.loc[str(previous_year)], 2),
                                       name=str(previous_year), hovertemplate='%{y:.0f}' + '<br>%{x}')
            fatturato_fig.update_yaxes(title_text='Fatturato')
            margine_fig.update_yaxes(title_text='Margine')
            ordini_fig.update_yaxes(title_text='N. Ordini')
        dff2 = df[df.index.year == year]
        return ['Il fatturato per l\'anno selezionato è pari a € ' + str(round(Fatturato[str(year)].sum(), 2)),
                fatturato_fig, margine_fig, ordini_fig, dcc.Dropdown(id='channel_dropdown', multi=False,
                                                                     options=[{'label': x, 'value': (x)} for x in
                                                                              sorted(dff2.Origine.unique())],
                                                                     placeholder='Origine'), mktpl, ordini]
    else:
        return [fatturato, fatturato_fig, margine_fig, ordini_fig, dcc.Dropdown(id='channel_dropdown'),
                mktpl, ordini]


if __name__ == '__main__':
    app.run_server(debug=True)
