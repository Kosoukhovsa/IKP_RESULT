"""
Дашборд для анализа количественных показателей по группе
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
from .global_style import GLOBAL_STYLE, CARD_STYLE

nav = Navbar()
# Фильтры

## По группе
filter_group = dcc.Dropdown(  
  multi=True,
  placeholder='Выберите группу',
  id = 'html_filter_group')

## По показателю
filter_kf = dcc.Dropdown(  
  multi=False,
  placeholder='Выберите показатель',
  id = 'html_filter_kf')


# Таблица с общей статистикой
card_table_1 = dbc.Card(
        dbc.CardBody([
            html.H4('Статистика показателя', className="card-title"),
            html.Div(id='html_output_table')#, style={'marginLeft': 15}
                      ]
                    ), color="light", outline=True
               )
# График
card_graph_1 = dbc.Card(
        dbc.CardBody([
            html.H4('Распределение показателя', className="card-title"),
            dcc.Graph(id = 'kf_output_graph')
                      ]
                    ), color="light", outline=True
               )

# Результат t-test
card_text_1 = dbc.Card(
        dbc.CardBody([
            html.H4('Влияние группы на значение показателя', className="card-title"),
            html.Div(id='html_output_text')#, style={'marginLeft': 15}
                      ]
                    ), color="light", outline=True
               )

# Общая статистика
layout = html.Div(style=GLOBAL_STYLE, children=[
    nav,
    html.Div(id='html_hidden_div', style = {'display': 'block'}), 
      
    dbc.Row([      
      dbc.Col([
          html.Label('Группа исследования'),
          html.Div( filter_group)], width=2),          
      dbc.Col([
          html.Label('Анализируемый показатель'),
          html.Div( filter_kf)], width=8),          
          ], style={'marginTop': 15, 'marginBottom': 15, 'marginLeft': 10}),

    dbc.Row(
      dbc.Col(card_table_1, width=10),style=CARD_STYLE
            ),
    dbc.Row(
      dbc.Col(card_graph_1, width=10),style=CARD_STYLE
            ),
    dbc.Row(
      dbc.Col(card_text_1, width=10),style=CARD_STYLE
            )
    ])
