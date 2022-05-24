import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import plotly.graph_objs as go
import pandas as pd
from datetime import datetime as dt
import dash_table
from .navbar import Navbar
from .global_style import GLOBAL_STYLE

nav = Navbar()
# Общий анализ без разбиения на группы

layout = html.Div(style=GLOBAL_STYLE, children=[
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
      ),style={'marginTop': 15, 'marginBottom': 15, 'marginLeft': 15}),     
        ]),
dbc.Row(
  dbc.Col(
  dbc.Card(
    dbc.CardBody([        
        html.Div(id='html_output_table')#, style={'marginLeft': 15}
                  ]
                ), color="light", outline=True
          )
        )
       ),      
#dbc.Row([
#    dbc.Col( 
#              html.Div(id='html_output_table'), style={'marginLeft': 15}, 
#            )
#        ]),
        ]
        )
