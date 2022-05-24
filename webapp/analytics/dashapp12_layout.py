"""
Дашборд для вывода общего количества пациентов
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
# Фильтры

filter_sex = dcc.Dropdown(
  options = [
  {'label':'Мужской', 'value':'M'},
  {'label':'Женский', 'value':'F'}
  #{'label':'Все', 'value':'ALL'}
  ],
  value=['M','F'],
  multi=True,
  placeholder='Выберите пол',
  id='html_filter_sex')

filter_group = dcc.Dropdown(  
  multi=True,
  placeholder='Выберите группу',
  id = 'html_filter_group')

# Таблица с общей статистикой
card_table_1 = dbc.Card(
        dbc.CardBody([
            html.H4('Общая статистика', className="card-title"),
            html.Div(id='html_output_table')#, style={'marginLeft': 15}
                      ]
                    )
               )


# Общая статистика
layout = html.Div(style=GLOBAL_STYLE, children=[
    nav,
    html.Div(id='html_hidden_div', style = {'display': 'block'}),    
    dbc.Row([      
      dbc.Col([
          html.Label('Пол пациента'),
          html.Div( filter_sex)], width=2),          
      dbc.Col([
          html.Label('Группа исследования'),
          html.Div( filter_group)], width=10),          
          ], style={'marginTop': 15, 'marginBottom': 15, 'marginLeft': 5, 'marginLeft': 10}),
    dbc.Row(
      dbc.Col(card_table_1, width=12)
            )
    ])
