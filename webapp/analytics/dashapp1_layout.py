import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objs as go
import pandas as pd

# Общий анализ без разбиения на группы

layout = html.Div([
html.H1('Показатели'),
dcc.Dropdown(
    id='dropdown-sex',
    options=[
    {'label':'Мужчины', 'value':'Муж.'},
    {'label':'Женщины', 'value':'Жен.'}
    ],
    value = 'Муж.'
),
dcc.Graph(
id = 'Box1',
figure = {
    'layout':go.Layout(
    title = 'распределение роста',
    xaxis = {'title':'X'},
    yaxis = {'title':'Y'},
    hovermode = 'closest')
        } ) ] )
