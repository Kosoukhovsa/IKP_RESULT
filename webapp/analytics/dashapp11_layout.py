import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import plotly.graph_objs as go
import pandas as pd
from datetime import datetime as dt
import dash_table
from .navbar import Navbar

nav = Navbar()
# Общий анализ без разбиения на группы
'''
layout = html.Div([
nav,
html.H1('Общие сведения за период'),
dcc.DatePickerRange(
    id='html_input_date_range',
    min_date_allowed = dt(2010,1,1),
    max_date_allowed = dt(2099,1,1),
    start_date=dt(2020, 1, 1).date(),
    end_date=dt(2020, 12, 31).date()
),
html.Div(id='html_output_table', style = {'margin':10, 'padding':10})
])
'''
layout = html.Div([
nav,
dbc.Row(dbc.Col(html.H3('Реестр пациентов'), width={'size':6,'offset':3}, style={'marginTop': 30, 'marginBottom': 15})),
dbc.Row([
    dbc.Col(html.Div(
    dcc.DatePickerRange(
        id='html_input_date_range',
        min_date_allowed = dt(2010,1,1),
        max_date_allowed = dt(2099,1,1),
        start_date=dt(2020, 1, 1).date(),
        end_date=dt(2020, 12, 31).date() ),
      ),style={'marginTop': 30, 'marginBottom': 15})
        ]),
dbc.Row([
    dbc.Col(html.Div(id='html_output_table'))
        ]),
        ])
