import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import plotly.graph_objs as go
import pandas as pd
from datetime import datetime as dt
import dash_table
from webapp import db
from .navbar import Navbar

colors = {
    'background': '#F0F8FF',
    'text': '#000000'
}

global_stile = {
'backgroundColor': colors['background'],
'color': colors['text'],

}

nav = Navbar()
# Фильтры
date_filter =  dcc.DatePickerRange(
            id='html_input_date_range',
            min_date_allowed = dt(2010,1,1),
            max_date_allowed = dt(2099,1,1),
            start_date=dt(2020, 1, 1).date(),
            end_date=dt(2020, 12, 31).date() 
                          )
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
  #options=[
  #{'label':'Мануальная техника', 'value':'Мануальная техника'},
  #{'label':'Робот-ассистированная (компьютерная навигация) техника', 
  # 'value':'Робот-ассистированная (компьютерная навигация) техника'},
  #{'label':'Роботизированная техника операции', 'value':'Роботизированная техника операции'},
  #{'label':'Все', 'value':'All'}
  #],
  #options = df_r_groups.unique(),
  #value=[
  #  'Мануальная техника',
  #  'Робот-ассистированная (компьютерная навигация) техника',
  #  'Роботизированная техника операции'
  #  ],
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
layout = html.Div(style=global_stile, children=[
    nav,
    html.Div(id='html_hidden_div', style = {'display': 'block'}),
    #dbc.Row(dbc.Col(html.H3('Общая статистика'), 
    #                style={'marginTop': 15, 'marginBottom': 15},
    #                width=3
    #                ),  justify="center"),
    #dbc.Row([dbc.Col(html.H5('Период открытия истории болезни'), width=4),
    #         dbc.Col(html.Div( date_filter), width=4),
    #        ],style={'marginTop': 15, 'marginBottom': 15, 'marginLeft': 5, 'marginLeft': 10}),
    dbc.Row([
      #dbc.Col(html.H5('Период открытия истории болезни')),
      #dbc.Col(html.Div( date_filter), width=3),
          #style={'marginTop': 15, 'marginBottom': 15, 'marginLeft': 5}, width=4),
      dbc.Col([
          html.Label('Пол пациента'),
          html.Div( filter_sex)], width=2),
          #style={'marginTop': 15, 'marginBottom': 15, 'marginLeft': 5}, width=4),
      dbc.Col([
          html.Label('Группа исследования'),
          html.Div( filter_group)], width=10),
          #style={'marginTop': 15, 'marginBottom': 15, 'marginLeft': 5}, width=4),
          ], style={'marginTop': 15, 'marginBottom': 15, 'marginLeft': 5, 'marginLeft': 10}),
    dbc.Row(
      dbc.Col(card_table_1, width=12)

      #dbc.Col(html.Div(id='html_output_table'), 
      #              style={'marginLeft': 20},
      #              width=6)
            )
    ])
