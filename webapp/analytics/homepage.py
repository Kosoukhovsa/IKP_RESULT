import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from .navbar import Navbar

# Это главная страница аналитического приложения
nav = Navbar()

body = dbc.Container([
        dbc.Row(
        [
            dbc.Col([],md=4),
            dbc.Col([],md=4)
        ]
        )
    ])

def HomePage():
    layout = html.Div([nav, body])
    return layout
