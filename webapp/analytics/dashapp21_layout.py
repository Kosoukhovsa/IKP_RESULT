"""
Дашборд: общие сведения по группам
"""

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import plotly.graph_objs as go
import pandas as pd
from datetime import datetime as dt
import dash_table
from webapp import db
from .navbar import Navbar
from .global_style import GLOBAL_STYLE

nav = Navbar()

# Таблица с общей статистикой
card_table_1 = dbc.Card(
        dbc.CardBody([
            html.H4('Общая статистика по группам', className="card-title"),
            html.Div(id='html_output_table')#, style={'marginLeft': 15}
                      ]
                    )
               )

# Общая статистика
layout = html.Div(style=GLOBAL_STYLE, children=[
    nav,  
    html.Div(id='html_hidden_div', style = {'display': 'block'}),   
    dbc.Row(
      dbc.Col(card_table_1, width=12)
            )
    ])

